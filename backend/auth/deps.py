"""Auth dependencies: API key, JWT, tenant, RBAC."""
from dataclasses import dataclass
from typing import Literal, Optional

from fastapi import Depends, Header, HTTPException

from backend.auth.constants import ROLE_HIERARCHY, Role, _parse_bearer, _role_from_value
from backend.auth.jwt import decode_access_token
from backend.auth.roles import resolve_api_key_role
from backend.config import get_config


@dataclass
class AuthContext:
    tenant_id: str
    role: Role
    auth_method: Literal["api_key", "jwt"]


def require_api_key(x_nexus_key: Optional[str] = Header(None, alias="X-Nexus-Key")) -> str:
    """Used by token issuance and legacy callers."""
    config = get_config()
    if not x_nexus_key or x_nexus_key != config.nexus_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_nexus_key


async def require_auth(
    authorization: Optional[str] = Header(None),
    x_nexus_key: Optional[str] = Header(None, alias="X-Nexus-Key"),
    x_nexus_tenant_id: Optional[str] = Header(None, alias="X-Nexus-Tenant-Id"),
    x_nexus_role: Optional[str] = Header("viewer", alias="X-Nexus-Role"),
) -> AuthContext:
    config = get_config()
    bearer = _parse_bearer(authorization)

    if bearer and config.auth_mode != "api_key_only":
        claims = decode_access_token(config, bearer)
        if claims:
            tenant = str(claims.get("sub") or x_nexus_tenant_id or "default")
            role = _role_from_value(str(claims.get("role", "viewer")))
            return AuthContext(tenant_id=tenant, role=role, auth_method="jwt")
        if config.auth_mode != "api_key_only":
            raise HTTPException(status_code=401, detail="Invalid token")

    if x_nexus_key and x_nexus_key == config.nexus_api_key:
        if config.auth_mode == "jwt_required":
            raise HTTPException(status_code=401, detail="JWT required")
        tenant = x_nexus_tenant_id or "default"
        role = resolve_api_key_role(config, x_nexus_role)
        return AuthContext(tenant_id=tenant, role=role, auth_method="api_key")

    raise HTTPException(status_code=401, detail="Authentication required")


def get_current_tenant(auth: AuthContext = Depends(require_auth)) -> str:
    return auth.tenant_id


def require_role(min_role: Role):
    async def _check(auth: AuthContext = Depends(require_auth)) -> Role:
        if ROLE_HIERARCHY.get(auth.role, 0) < ROLE_HIERARCHY[min_role]:
            raise HTTPException(status_code=403, detail=f"Requires role {min_role}")
        return auth.role

    return _check
