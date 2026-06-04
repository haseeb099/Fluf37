from fastapi import APIRouter, Depends
from fastapi.responses import Response

from backend.auth.deps import require_api_key, require_role
from backend.utils.audit_log import AuditLog

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


@router.get("/export")
async def export_audit(_: str = Depends(require_api_key), __: str = Depends(require_role("admin"))):
    log = AuditLog()
    return Response(content=log.export(), media_type="application/json")


@router.get("/verify")
async def verify_audit(_: str = Depends(require_api_key)):
    return AuditLog().verify().model_dump()
