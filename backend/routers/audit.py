from fastapi import APIRouter, Depends
from fastapi.responses import Response

from backend.auth.deps import AuthContext, require_auth, require_role
from backend.utils.audit_log import AuditLog

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


@router.get("/export")
async def export_audit(
    _auth: AuthContext = Depends(require_auth), __: str = Depends(require_role("admin"))
):
    log = AuditLog()
    return Response(content=log.export(), media_type="application/json")


@router.get("/verify")
async def verify_audit(_auth: AuthContext = Depends(require_auth)):
    return AuditLog().verify().model_dump()


@router.get("/recent")
async def recent_audit(
    limit: int = 50,
    _auth: AuthContext = Depends(require_auth),
    __: str = Depends(require_role("analyst")),
):
    entries = AuditLog().tail(min(limit, 200))
    return {"entries": entries, "count": len(entries)}
