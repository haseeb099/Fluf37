from backend.main import app
from starlette.testclient import TestClient


def test_ready_after_startup():
    with TestClient(app) as client:
        r = client.get("/ready")
        assert r.status_code == 200
        body = r.json()
        assert body.get("ready") is True
        assert "memory" in body
        assert body.get("connectors_registered", 0) >= 1
