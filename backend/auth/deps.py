"""Auth dependencies: API key, tenant, RBAC."""
from typing import Literal, Optional

from fastapi import Header, HTTPException, Request

from backend.config import get_config

Role = Literal["admin", "analyst", "viewer"]


def require_api_key(x_nexus_key: Optional[str] = Header(None, alias="X-Nexus-Key")) -> str:
    config = get_config()
    if not x_nexus_key or x_nexus_key != config.nexus_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_nexus_key


def get_current_tenant(
    x_nexus_tenant_id: Optional[str] = Header(None, alias="X-Nexus-Tenant-Id"),
) -> str:
    return x_nexus_tenant_id or "default"


def require_role(min_role: Role):
    hierarchy = {"viewer": 0, "analyst": 1, "admin": 2}

    async def _check(
        request: Request,
        x_nexus_role: Optional[str] = Header("admin", alias="X-Nexus-Role"),
    ) -> Role:
        role: Role = x_nexus_role if x_nexus_role in hierarchy else "viewer"  # type: ignore
        if hierarchy.get(role, 0) < hierarchy[min_role]:
            raise HTTPException(status_code=403, detail=f"Requires role {min_role}")
        return role

    return _check
