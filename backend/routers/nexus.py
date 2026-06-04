from fastapi import APIRouter, Depends, Request

from backend.auth.deps import AuthContext, get_current_tenant, require_auth
from backend.rate_limit import limiter

router = APIRouter(prefix="/api/v1/nexus", tags=["Nexus"])


@router.post("/run/demo")
@limiter.limit("30/minute")
async def run_demo(
    request: Request,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
):
    from backend.main import get_orchestrator
    orch = get_orchestrator(tenant)
    events = []
    async for event in orch.run_pipeline(mode="demo"):
        events.append(event.model_dump(mode="json"))
    return {"status": "accepted", "pipeline_state": orch.pipeline_state, "events_count": len(events)}


@router.get("/status")
async def pipeline_status(
    request: Request,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
):
    from backend.main import get_orchestrator
    orch = get_orchestrator(tenant)
    return {"pipeline_state": orch.pipeline_state, "context_keys": list(orch.context.keys())}
