"""Role resolution — JWT is authoritative; API-key role headers are demo-only."""
from typing import Optional

from backend.auth.constants import ROLE_HIERARCHY, Role, _parse_bearer, _role_from_value
from backend.auth.jwt import decode_access_token
from backend.config import NexusConfig


def resolve_api_key_role(config: NexusConfig, header_role: Optional[str]) -> Role:
    """Role for X-Nexus-Key requests. Ignores client role unless trust_client_role()."""
    if config.trust_client_role():
        return _role_from_value(header_role)
    return "viewer"


def resolve_token_role(
    config: NexusConfig,
    authorization: Optional[str],
    requested_role: Optional[str],
) -> Role:
    """Role embedded in newly issued JWTs."""
    requested = _role_from_value(requested_role)
    if config.trust_client_role():
        return requested
    if requested == "viewer":
        return "viewer"
    bearer = _parse_bearer(authorization)
    if not bearer:
        return "viewer"
    claims = decode_access_token(config, bearer)
    if not claims:
        return "viewer"
    caller_role = _role_from_value(str(claims.get("role", "viewer")))
    if ROLE_HIERARCHY.get(caller_role, 0) >= ROLE_HIERARCHY["admin"]:
        return requested
    if ROLE_HIERARCHY.get(caller_role, 0) >= ROLE_HIERARCHY["analyst"] and requested == "analyst":
        return "analyst"
    return "viewer"
