from backend.auth.jwt import create_access_token
from backend.main import _resolve_ws_tenant

_SECRET = "test-secret-at-least-32-characters"


def test_resolve_ws_tenant_from_jwt_sub(monkeypatch):
    from backend.config import get_config

    get_config.cache_clear()
    monkeypatch.setenv("JWT_SECRET", _SECRET)
    cfg = get_config()
    token = create_access_token(cfg, "tenant_acme", "analyst")
    assert _resolve_ws_tenant(token) == "tenant_acme"
    get_config.cache_clear()


def test_resolve_ws_tenant_defaults_for_api_key(monkeypatch):
    from backend.config import get_config

    get_config.cache_clear()
    monkeypatch.setenv("JWT_SECRET", _SECRET)
    monkeypatch.setenv("NEXUS_API_KEY", "my-key")
    get_config()
    assert _resolve_ws_tenant("my-key") == "default"
    get_config.cache_clear()
