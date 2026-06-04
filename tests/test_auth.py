import pytest
from backend.auth.jwt import create_access_token, decode_access_token
from backend.config import NexusConfig
from backend.main import app
from httpx import ASGITransport, AsyncClient

API_HEADERS = {"X-Nexus-Key": "demo-key"}


@pytest.mark.asyncio
async def test_issue_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/auth/token", headers=API_HEADERS)
        assert r.status_code == 200
        body = r.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"]


@pytest.mark.asyncio
async def test_protected_route_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/sources/status")
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_jwt_on_protected_route():
    config = NexusConfig(nexus_demo_mode=True, nexus_api_key="demo-key")
    token = create_access_token(config, "default", "viewer")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get(
            "/api/v1/sources/status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200


def test_decode_token_roundtrip():
    config = NexusConfig(jwt_secret="test-secret", jwt_expire_minutes=30)
    token = create_access_token(config, "tenant-a", "analyst")
    claims = decode_access_token(config, token)
    assert claims is not None
    assert claims["sub"] == "tenant-a"
    assert claims["role"] == "analyst"


@pytest.mark.asyncio
async def test_viewer_cannot_connect_source():
    headers = {
        "X-Nexus-Key": "demo-key",
        "X-Nexus-Role": "viewer",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/connect/crm", headers=headers)
        assert r.status_code == 403
