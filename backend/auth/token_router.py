from typing import Optional

from fastapi import APIRouter, Depends, Header

from backend.auth.deps import require_api_key
from backend.auth.jwt import create_access_token
from backend.auth.roles import resolve_token_role
from backend.config import get_config

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/token")
async def issue_token(
    _: str = Depends(require_api_key),
    x_nexus_tenant_id: Optional[str] = Header(None, alias="X-Nexus-Tenant-Id"),
    x_nexus_role: Optional[str] = Header("viewer", alias="X-Nexus-Role"),
    authorization: Optional[str] = Header(None),
):
    config = get_config()
    tenant = x_nexus_tenant_id or "default"
    role = resolve_token_role(config, authorization, x_nexus_role)
    token = create_access_token(config, tenant, role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role,
        "tenant_id": tenant,
        "trust_client_role": config.trust_client_role(),
    }
