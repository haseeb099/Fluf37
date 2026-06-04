from fastapi import APIRouter, Depends, HTTPException

from backend.auth.deps import require_api_key
from backend.schemas.models import OutcomeRequest

router = APIRouter(prefix="/api/v1/decisions", tags=["Decisions"])


@router.get("/")
async def list_decisions(_: str = Depends(require_api_key)):
    from backend.main import get_memory
    decisions = await get_memory().timeseries.get_decisions()
    return [d.model_dump() for d in decisions]


@router.get("/{decision_id}")
async def get_decision(decision_id: str, _: str = Depends(require_api_key)):
    from backend.main import get_memory
    for d in await get_memory().timeseries.get_decisions():
        if d.id == decision_id:
            return d.model_dump()
    raise HTTPException(status_code=404, detail="Decision not found")


@router.post("/{decision_id}/outcome")
async def submit_outcome(decision_id: str, body: OutcomeRequest, _: str = Depends(require_api_key)):
    from backend.main import get_memory
    await get_memory().timeseries.update_decision_outcome(decision_id, body.outcome)
    return {"updated": decision_id, "outcome": body.outcome}
