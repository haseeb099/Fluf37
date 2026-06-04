"""Shared slowapi limiter."""
from slowapi import Limiter
from slowapi.util import get_remote_address


def _rate_limit_key(request):
    key = request.headers.get("X-Nexus-Key")
    if key:
        return f"key:{key}"
    auth = request.headers.get("Authorization", "")
    if auth:
        return f"auth:{auth[:40]}"
    return get_remote_address(request)


def build_limiter() -> Limiter:
    from backend.config import get_config

    cfg = get_config()
    return Limiter(key_func=_rate_limit_key, default_limits=[cfg.get_rate_limit()])


limiter = build_limiter()
