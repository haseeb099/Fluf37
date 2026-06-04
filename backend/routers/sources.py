from fastapi import APIRouter, Depends, HTTPException, Request

from backend.auth.deps import AuthContext, Role, get_current_tenant, require_auth, require_role
from backend.schemas.models import SourceType

router = APIRouter(prefix="/api/v1", tags=["Integrations"])


@router.get("/sources/status")
async def sources_status(
    request: Request,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
):
    from backend.main import get_connection_manager
    mgr = get_connection_manager(tenant)
    return {"sources": [s.model_dump() for s in mgr.get_all_status()]}


@router.post("/connect/{source}")
async def connect_source(
    request: Request,
    source: SourceType,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
    __: Role = Depends(require_role("admin")),
):
    from backend.main import get_connection_manager
    mgr = get_connection_manager(tenant)
    try:
        status = await mgr.connect(source)
        return status.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/connect/{source}")
async def disconnect_source(
    request: Request,
    source: SourceType,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
    __: Role = Depends(require_role("admin")),
):
    from backend.main import get_connection_manager
    mgr = get_connection_manager(tenant)
    await mgr.disconnect(source)
    return {"disconnected": source}


@router.post("/connect/{source}/sync")
async def sync_source(
    request: Request,
    source: SourceType,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
    ___: Role = Depends(require_role("analyst")),
):
    from backend.main import get_connection_manager
    mgr = get_connection_manager(tenant)
    partial, result = await mgr.sync_source(source)
    return {"sync": result.model_dump(), "records": len(partial.crm) + len(partial.bank)}


@router.get("/connectors")
async def list_connectors(
    request: Request, _auth: AuthContext = Depends(require_auth)
):
    from backend.config import get_config
    from backend.integration.registry import ConnectorRegistry
    reg = ConnectorRegistry(get_config())
    return {
        "types": reg.list_types(),
        "capabilities": reg.describe_all(),
    }
