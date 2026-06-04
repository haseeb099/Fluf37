"""Plugin marketplace API tests."""
import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


HEADERS = {"X-Nexus-Key": "demo-key", "X-Nexus-Role": "viewer"}
ADMIN = {"X-Nexus-Key": "demo-key", "X-Nexus-Role": "admin"}


@pytest.mark.asyncio
async def test_list_plugins_catalog(client):
    r = await client.get("/api/v1/plugins", headers=HEADERS)
    assert r.status_code == 200
    body = r.json()
    assert body["summary"]["total"] >= 7
    assert body["summary"]["official"] >= 7
    assert any(p["id"] == "nexus-crm" for p in body["plugins"])


@pytest.mark.asyncio
async def test_register_community_plugin(client, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGIN_STORE_PATH", str(tmp_path / "registered.json"))
    from backend.config import get_config

    get_config.cache_clear()
    payload = {
        "name": "Acme ERP Bridge",
        "description": "Push ERP vendor payments via signed webhook for nightly risk review.",
        "category": "finance",
        "integration_type": "webhook",
        "vendor": "Acme Corp IT",
        "webhook_source": "acme_erp",
    }
    r = await client.post("/api/v1/plugins/register", json=payload, headers=ADMIN)
    assert r.status_code == 200
    body = r.json()
    assert body["id"].startswith("custom-")
    assert body["tier"] == "community"
    assert body["supports_webhook"] is True

    r2 = await client.get("/api/v1/plugins", headers=HEADERS)
    ids = [p["id"] for p in r2.json()["plugins"]]
    assert body["id"] in ids


@pytest.mark.asyncio
async def test_plugin_detail_not_found(client):
    r = await client.get("/api/v1/plugins/does-not-exist", headers=HEADERS)
    assert r.status_code == 404
