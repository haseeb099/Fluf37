import pytest
from backend.main import app
from httpx import ASGITransport, AsyncClient


def test_health_liveness():
    """Liveness works without lifespan (import-time app)."""
    import asyncio

    async def _get():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            return await client.get("/health")

    r = asyncio.run(_get())
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_after_startup():
    from starlette.testclient import TestClient

    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body.get("ready") is True
        assert "version" in body


@pytest.mark.asyncio
async def test_sources_status():
    headers = {"X-Nexus-Key": "demo-key"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/sources/status", headers=headers)
        assert r.status_code == 200
