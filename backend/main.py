"""Nexus AI FastAPI application."""
import json
from contextlib import asynccontextmanager
from typing import Dict, Optional

import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.agents.orchestrator import NexusOrchestrator, WebSocketManager
from backend.auth.jwt import decode_access_token
from backend.auth.token_router import router as auth_router
from backend.config import get_config
from backend.integration.connection_manager import ConnectionManager
from backend.integration.credential_store import CredentialStore
from backend.memory.layer import MemoryLayer
from backend.rate_limit import limiter
from backend.routers import audit, decisions, evolution, ingest, memory, nexus, sources
from backend.schemas.models import WSClientMessage
from backend.utils.llm_client import LLMClient

logger = structlog.get_logger()

# Per-tenant orchestrators share one MemoryLayer today (Scale: per-tenant DB/pgvector).
_memory: MemoryLayer | None = None
_orchestrators: Dict[str, NexusOrchestrator] = {}
_connection_managers: Dict[str, ConnectionManager] = {}
_ws_manager = WebSocketManager()
_credentials = CredentialStore()
_ready = False


config = get_config()


def _ws_auth_required() -> bool:
    return config.nexus_ws_require_auth or (
        config.auth_mode == "jwt_required" and not config.is_demo()
    )


def _authenticate_ws_token(token: Optional[str]) -> bool:
    if not token:
        return False
    if token == config.nexus_api_key:
        return True
    return decode_access_token(config, token) is not None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _memory, _ready
    config = get_config()
    _memory = MemoryLayer(config)
    await _memory.initialize_demo()
    mgr = ConnectionManager(config)
    await mgr.sync_all(demo=True)
    _connection_managers["default"] = mgr
    _orchestrators["default"] = NexusOrchestrator(
        config, _memory, LLMClient(config), mgr, _ws_manager
    )
    _ready = True
    logger.info("nexus_started", demo_mode=config.is_demo())
    yield
    if _memory:
        _memory.get_graph().save()
    _ready = False


app = FastAPI(title="Nexus AI", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(nexus.router)
app.include_router(sources.router)
app.include_router(memory.router)
app.include_router(decisions.router)
app.include_router(evolution.router)
app.include_router(ingest.router)
app.include_router(audit.router)


def get_memory() -> MemoryLayer:
    assert _memory is not None
    return _memory


def get_connection_manager(tenant_id: str = "default") -> ConnectionManager:
    if tenant_id not in _connection_managers:
        cfg = get_config()
        _connection_managers[tenant_id] = ConnectionManager(cfg, tenant_id)
    return _connection_managers[tenant_id]


def get_orchestrator(tenant_id: str = "default") -> NexusOrchestrator:
    if tenant_id not in _orchestrators:
        cfg = get_config()
        mgr = get_connection_manager(tenant_id)
        _orchestrators[tenant_id] = NexusOrchestrator(
            cfg, get_memory(), LLMClient(cfg), mgr, _ws_manager
        )
    return _orchestrators[tenant_id]


@app.get("/health")
async def health():
    agent_states = {}
    orch = _orchestrators.get("default")
    if _ready and orch is not None:
        agent_states = {aid: agent.state.value for aid, agent in orch.agents.items()}
    return {"status": "ok", "demo_mode": config.is_demo(), "agents": agent_states}


@app.get("/ready")
async def ready():
    if not _ready or _memory is None:
        return {"ready": False, "reason": "initializing"}
    stats = await _memory.get_stats()
    return {
        "ready": True,
        "connectors_registered": len(config.get_enabled_connectors()),
        "memory": stats.model_dump(),
    }


@app.websocket("/ws/nexus/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    _ws_manager.connections.append(websocket)
    ws_authenticated = not _ws_auth_required()
    query_token = websocket.query_params.get("token")
    if query_token and _authenticate_ws_token(query_token):
        ws_authenticated = True
    try:
        while True:
            raw = await websocket.receive_text()
            msg = WSClientMessage.model_validate(json.loads(raw))
            if msg.type == "AUTH":
                if _authenticate_ws_token(msg.token):
                    ws_authenticated = True
                    await websocket.send_json({
                        "type": "PIPELINE_STATE",
                        "agent_id": "system",
                        "data": {"state": "AUTHENTICATED"},
                    })
                else:
                    await websocket.send_json({
                        "type": "AGENT_ERROR",
                        "agent_id": "system",
                        "data": "invalid_token",
                    })
                continue
            if msg.type == "PING":
                await websocket.send_json({"type": "PONG", "agent_id": "system", "data": {}})
                continue
            if msg.type == "RUN_PIPELINE":
                if _ws_auth_required() and not ws_authenticated:
                    await websocket.send_json({
                        "type": "AGENT_ERROR",
                        "agent_id": "orchestrator",
                        "data": "authentication_required",
                    })
                    continue
                orch = get_orchestrator()
                async for event in orch.run_pipeline(mode=msg.mode or "demo"):
                    await websocket.send_json(event.model_dump(mode="json"))
                report = orch.aggregate_results()
                await websocket.send_json({
                    "type": "PIPELINE_STATE",
                    "agent_id": "orchestrator",
                    "data": {"state": "COMPLETE", "report": report.model_dump(mode="json")},
                })
            elif msg.type == "RESET":
                orch = get_orchestrator()
                orch.context.clear()
                orch.pipeline_state = "IDLE"
    except WebSocketDisconnect:
        if websocket in _ws_manager.connections:
            _ws_manager.connections.remove(websocket)
