from fastapi import APIRouter, Depends, HTTPException

from backend.auth.deps import AuthContext, Role, require_auth, require_role
from backend.schemas.models import OutcomeRequest

router = APIRouter(prefix="/api/v1/decisions", tags=["Decisions"])


@router.get("/")
async def list_decisions(_auth: AuthContext = Depends(require_auth)):
    from backend.main import get_memory
    decisions = await get_memory().timeseries.get_decisions()
    return [d.model_dump() for d in decisions]


@router.get("/{decision_id}")
async def get_decision(decision_id: str, _auth: AuthContext = Depends(require_auth)):
    from backend.main import get_memory
    for d in await get_memory().timeseries.get_decisions():
        if d.id == decision_id:
            return d.model_dump()
    raise HTTPException(status_code=404, detail="Decision not found")


@router.post("/{decision_id}/outcome")
async def submit_outcome(
    decision_id: str,
    body: OutcomeRequest,
    _auth: AuthContext = Depends(require_auth),
    __: Role = Depends(require_role("analyst")),
):
    from backend.main import get_memory
    await get_memory().timeseries.update_decision_outcome(decision_id, body.outcome)
    return {"updated": decision_id, "outcome": body.outcome}
