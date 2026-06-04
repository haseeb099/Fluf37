"""Shared auth constants (no FastAPI deps — avoids circular imports)."""
from typing import Literal, Optional

Role = Literal["admin", "analyst", "viewer"]
ROLE_HIERARCHY = {"viewer": 0, "analyst": 1, "admin": 2}


def _parse_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


def _role_from_value(role: Optional[str]) -> Role:
    if role in ROLE_HIERARCHY:
        return role  # type: ignore[return-value]
    return "viewer"
