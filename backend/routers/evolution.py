from fastapi import APIRouter, Depends

from backend.auth.deps import require_api_key, require_role
from backend.schemas.models import EvolutionCycle

router = APIRouter(prefix="/api/v1/evolution", tags=["Evolution"])


@router.get("/report")
async def evolution_report(_: str = Depends(require_api_key)):
    from backend.agents.evolution import EvolutionAgent, EvolutionInput
    from backend.main import get_orchestrator
    orch = get_orchestrator()
    agent = orch.agents["evolution"]
    report_data = None
    async for event in agent.run(EvolutionInput(decisions_count=2)):
        if event.type == "AGENT_COMPLETE":
            report_data = event.data
    return report_data


@router.post("/approve/{cycle_id}")
async def approve_evolution(
    cycle_id: str,
    _: str = Depends(require_api_key),
    __: str = Depends(require_role("admin")),
):
    from backend.main import get_memory
    cycle = EvolutionCycle(id=cycle_id, approved=True, weight_changes={"forcing": 0.30})
    await get_memory().timeseries.record_evolution(cycle)
    return {"approved": cycle_id}
