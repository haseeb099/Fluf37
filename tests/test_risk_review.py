from backend.main import app
from starlette.testclient import TestClient


def test_risk_review_run_returns_artifact():
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/risk-review/run",
            headers={"X-Nexus-Key": "demo-key", "X-Nexus-Role": "analyst"},
        )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["summary"]["workflow"] == "pre_release_risk_review"
    assert body["summary"]["status"] == "complete"
    assert body["summary"]["blind_spots_count"] >= 1
    assert len(body["findings"]) >= 1
    assert body["summary"]["data_mode"] == "synthetic"


def test_risk_review_requires_analyst():
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/risk-review/run",
            headers={"X-Nexus-Key": "demo-key", "X-Nexus-Role": "viewer"},
        )
    assert res.status_code == 403


def test_platform_info():
    with TestClient(app) as client:
        res = client.get(
            "/api/v1/platform/info",
            headers={"X-Nexus-Key": "demo-key"},
        )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["product_wedge"] == "Pre-Release Risk Review"
    assert body["launch_verdict"] in ("demo_ready", "pilot_ready")
    assert "connector_capabilities" in body
    assert isinstance(body["pilot_blockers"], list)
