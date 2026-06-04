from typing import Optional

from fastapi import APIRouter, Depends, Header

from backend.auth.deps import ROLE_HIERARCHY, get_current_tenant, require_api_key
from backend.auth.jwt import create_access_token
from backend.config import get_config

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/token")
async def issue_token(
    tenant: str = Depends(get_current_tenant),
    _: str = Depends(require_api_key),
    x_nexus_role: Optional[str] = Header("viewer", alias="X-Nexus-Role"),
):
    role = x_nexus_role if x_nexus_role in ROLE_HIERARCHY else "viewer"
    config = get_config()
    token = create_access_token(config, tenant, role)
    return {"access_token": token, "token_type": "bearer"}
