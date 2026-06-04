import pytest
from backend.main import app
from httpx import ASGITransport, AsyncClient

HEADERS = {"X-Nexus-Key": "demo-key", "X-Nexus-Tenant-Id": "ingest-test"}


@pytest.mark.asyncio
async def test_webhook_ingest_updates_connection_manager():
    payload = {
        "deals": [
            {
                "id": "deal-ingest-1",
                "company": "Ingested Co",
                "stage": "negotiation",
                "deal_value": 50000,
            }
        ]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/ingest/crm", json=payload, headers=HEADERS)
        assert r.status_code == 200
        body = r.json()
        assert body["ingested"] == "crm"
        assert body["records"] >= 1

        status = await client.get("/api/v1/sources/status", headers=HEADERS)
        assert status.status_code == 200
        sources = status.json()["sources"]
        crm = next((s for s in sources if s["source_type"] == "crm"), None)
        assert crm is not None
        assert crm["state"] in ("connected", "disconnected")
