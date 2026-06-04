from fastapi import APIRouter, Depends

from backend.auth.deps import get_current_tenant, require_api_key
from backend.schemas.models import RunPipelineRequest

router = APIRouter(prefix="/api/v1/nexus", tags=["Nexus"])


@router.post("/run/demo")
async def run_demo(tenant: str = Depends(get_current_tenant), _: str = Depends(require_api_key)):
    from backend.main import get_orchestrator
    orch = get_orchestrator(tenant)
    events = []
    async for event in orch.run_pipeline(mode="demo"):
        events.append(event.model_dump(mode="json"))
    return {"status": "accepted", "pipeline_state": orch.pipeline_state, "events_count": len(events)}


@router.get("/status")
async def pipeline_status(tenant: str = Depends(get_current_tenant), _: str = Depends(require_api_key)):
    from backend.main import get_orchestrator
    orch = get_orchestrator(tenant)
    return {"pipeline_state": orch.pipeline_state, "context_keys": list(orch.context.keys())}
