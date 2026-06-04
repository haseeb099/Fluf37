"""Pre-Release Risk Review — sellable workflow API."""
from fastapi import APIRouter, Depends, Request

from backend.auth.deps import AuthContext, Role, get_current_tenant, require_auth, require_role
from backend.config import get_config
from backend.rate_limit import limiter
from backend.schemas.models import RiskReviewReport
from backend.services.risk_review import build_risk_review_report

router = APIRouter(prefix="/api/v1/risk-review", tags=["Risk Review"])


@router.post("/run", response_model=RiskReviewReport)
@limiter.limit("20/minute")
async def run_risk_review(
    request: Request,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
    __: Role = Depends(require_role("analyst")),
):
    """Run the full pipeline and return a buyer-facing risk review artifact."""
    from backend.main import get_orchestrator

    config = get_config()
    orch = get_orchestrator(tenant)
    correlation_id = None
    async for event in orch.run_pipeline(mode="demo", tenant_id=tenant):
        if event.type == "PIPELINE_STATE" and isinstance(event.data, dict):
            correlation_id = event.data.get("correlation_id") or correlation_id
    report = orch.aggregate_results()
    return build_risk_review_report(report, config=config, correlation_id=correlation_id)
