"""
API tests for Kubernetes Liveness and Readiness probes.
"""

from fastapi.testclient import TestClient


def test_liveness_probe_healthy(client: TestClient):
    res = client.get("/health/live")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "alive"
    assert data["service"] == "titan-inventory-api"
    assert "timestamp" in data


def test_readiness_probe_healthy(client: TestClient):
    res = client.get("/health/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["details"]["database"]["healthy"] is True


def test_simulated_readiness_failure(client: TestClient):
    # Inject readiness failure via Reliability Lab test route
    auth_headers = {"X-Titan-Fault-Auth": "test-token-xyz"}
    client.post("/test/faults/probe", json={"probe_type": "readiness", "fail": True}, headers=auth_headers)

    # Readiness probe must now return 503 Service Unavailable
    res = client.get("/health/ready")
    assert res.status_code == 503
    assert res.json()["status"] == "not_ready"

    # Reset fault
    client.post("/test/faults/reset", headers=auth_headers)
    res_recovered = client.get("/health/ready")
    assert res_recovered.status_code == 200
    assert res_recovered.json()["status"] == "ready"


def test_simulated_liveness_failure(client: TestClient):
    auth_headers = {"X-Titan-Fault-Auth": "test-token-xyz"}
    client.post("/test/faults/probe", json={"probe_type": "liveness", "fail": True}, headers=auth_headers)

    # Liveness probe must return 500
    res = client.get("/health/live")
    assert res.status_code == 500
    assert res.json()["status"] == "unhealthy"

    # Reset fault
    client.post("/test/faults/reset", headers=auth_headers)
    res_recovered = client.get("/health/live")
    assert res_recovered.status_code == 200
