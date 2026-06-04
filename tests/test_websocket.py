"""WebSocket pipeline and auth behavior."""
from backend.config import get_config
from backend.main import app
from starlette.testclient import TestClient


def _run_pipeline_on_ws(websocket) -> set[str]:
    websocket.send_json({"type": "RUN_PIPELINE", "mode": "demo"})
    completes: set[str] = set()
    saw_complete = False
    for _ in range(300):
        data = websocket.receive_json()
        if data.get("type") == "AGENT_COMPLETE":
            completes.add(data.get("agent_id", ""))
        payload = data.get("data") or {}
        if (
            data.get("type") == "PIPELINE_STATE"
            and isinstance(payload, dict)
            and payload.get("state") == "COMPLETE"
        ):
            saw_complete = True
            break
    assert saw_complete, "pipeline did not reach COMPLETE"
    return completes


def test_websocket_run_pipeline_demo():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/nexus/stream") as ws:
            completes = _run_pipeline_on_ws(ws)
    assert "connector" in completes
    assert "silent_finder" in completes
    assert "evolution" in completes


def test_websocket_ping_pong():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/nexus/stream") as ws:
            ws.send_json({"type": "PING"})
            data = ws.receive_json()
    assert data.get("type") == "PONG"


def test_websocket_requires_auth_when_configured(monkeypatch):
    monkeypatch.setenv("NEXUS_WS_REQUIRE_AUTH", "true")
    get_config.cache_clear()
    try:
        with TestClient(app) as client:
            with client.websocket_connect("/ws/nexus/stream") as ws:
                ws.send_json({"type": "RUN_PIPELINE", "mode": "demo"})
                data = ws.receive_json()
        assert data.get("type") == "AGENT_ERROR"
        assert data.get("data") == "authentication_required"
    finally:
        monkeypatch.delenv("NEXUS_WS_REQUIRE_AUTH", raising=False)
        get_config.cache_clear()


def test_websocket_auth_with_api_key(monkeypatch):
    monkeypatch.setenv("NEXUS_WS_REQUIRE_AUTH", "true")
    get_config.cache_clear()
    cfg = get_config()
    try:
        with TestClient(app) as client:
            with client.websocket_connect(
                f"/ws/nexus/stream?token={cfg.nexus_api_key}"
            ) as ws:
                completes = _run_pipeline_on_ws(ws)
        assert "decision" in completes
    finally:
        monkeypatch.delenv("NEXUS_WS_REQUIRE_AUTH", raising=False)
        get_config.cache_clear()
