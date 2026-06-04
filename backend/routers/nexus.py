from fastapi import APIRouter, Depends, Request

from backend.auth.deps import AuthContext, Role, get_current_tenant, require_auth, require_role
from backend.rate_limit import limiter

router = APIRouter(prefix="/api/v1/nexus", tags=["Nexus"])


@router.post("/run/demo")
@limiter.limit("30/minute")
async def run_demo(
    request: Request,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
    __: Role = Depends(require_role("analyst")),
):
    from backend.main import get_orchestrator
    orch = get_orchestrator(tenant)
    events = []
    correlation_id = None
    async for event in orch.run_pipeline(mode="demo", tenant_id=tenant):
        payload = event.model_dump(mode="json")
        events.append(payload)
        if event.type == "PIPELINE_STATE" and isinstance(event.data, dict):
            correlation_id = event.data.get("correlation_id") or correlation_id
    return {
        "status": "accepted",
        "pipeline_state": orch.pipeline_state,
        "events_count": len(events),
        "correlation_id": correlation_id,
    }


@router.get("/status")
async def pipeline_status(
    request: Request,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
):
    from backend.main import get_orchestrator
    orch = get_orchestrator(tenant)
    return {"pipeline_state": orch.pipeline_state, "context_keys": list(orch.context.keys())}
