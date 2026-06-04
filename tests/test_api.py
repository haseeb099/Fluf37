import pytest
from backend.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_sources_status():
    headers = {"X-Nexus-Key": "demo-key"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/sources/status", headers=headers)
        assert r.status_code == 200
