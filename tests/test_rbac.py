import pytest
from backend.auth.jwt import create_access_token
from backend.auth.roles import resolve_api_key_role, resolve_token_role
from backend.config import NexusConfig
from backend.main import app
from httpx import ASGITransport, AsyncClient

API_HEADERS = {"X-Nexus-Key": "demo-key"}


def test_api_key_role_capped_when_not_trusted():
    config = NexusConfig.model_construct(
        nexus_demo_mode=False,
        nexus_pre_live_mode=True,
        nexus_trust_client_role=True,
        nexus_api_key="demo-key",
    )
    assert config.trust_client_role() is False
    assert resolve_api_key_role(config, "admin") == "viewer"


def test_api_key_role_honored_in_demo():
    config = NexusConfig(nexus_demo_mode=True, nexus_trust_client_role=True)
    assert resolve_api_key_role(config, "admin") == "admin"


def test_token_elevation_requires_admin_jwt():
    config = NexusConfig.model_construct(
        nexus_demo_mode=False,
        nexus_pre_live_mode=True,
        jwt_secret="s",
        nexus_api_key="k",
    )
    assert resolve_token_role(config, None, "admin") == "viewer"
    admin = create_access_token(config, "default", "admin")
    assert resolve_token_role(config, f"Bearer {admin}", "admin") == "admin"


@pytest.mark.asyncio
async def test_viewer_cannot_run_pipeline_demo():
    headers = {**API_HEADERS, "X-Nexus-Role": "viewer"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/nexus/run/demo", headers=headers)
        assert r.status_code == 403


@pytest.mark.asyncio
async def test_analyst_can_run_pipeline_demo():
    headers = {**API_HEADERS, "X-Nexus-Role": "analyst"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/nexus/run/demo", headers=headers)
        assert r.status_code == 200
        assert r.json().get("correlation_id")


@pytest.mark.asyncio
async def test_viewer_cannot_sync():
    headers = {**API_HEADERS, "X-Nexus-Role": "viewer"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/connect/crm/sync", headers=headers)
        assert r.status_code == 403
