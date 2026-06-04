import pytest
from backend.config import get_config
from backend.main import app
from backend.rate_limit import build_limiter
from httpx import ASGITransport, AsyncClient

HEADERS = {"X-Nexus-Key": "demo-key"}


@pytest.mark.asyncio
async def test_rate_limit_returns_429(monkeypatch):
    monkeypatch.setenv("NEXUS_RATE_LIMIT_DEMO_PER_MINUTE", "2")
    get_config.cache_clear()
    app.state.limiter = build_limiter()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for _ in range(2):
            r = await client.get("/api/v1/sources/status", headers=HEADERS)
            assert r.status_code == 200
        r = await client.get("/api/v1/sources/status", headers=HEADERS)
        assert r.status_code == 429
    get_config.cache_clear()
    app.state.limiter = build_limiter()
