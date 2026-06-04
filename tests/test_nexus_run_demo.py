from starlette.testclient import TestClient

from backend.main import app


def test_run_demo_endpoint_completes():
    with TestClient(app) as client:
        res = client.post("/api/v1/nexus/run/demo", headers={"X-Nexus-Key": "demo-key"})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["pipeline_state"] == "COMPLETE"
    assert body["events_count"] > 10
