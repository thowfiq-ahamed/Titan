"""
API tests for Controlled Test-Only Fault Injection.
"""

from fastapi.testclient import TestClient


def test_fault_injection_requires_auth(client: TestClient):
    # Without header
    res = client.post("/test/faults/probe", json={"probe_type": "liveness", "fail": True})
    assert res.status_code == 422 or res.status_code == 401

    # With invalid token
    res_bad = client.post(
        "/test/faults/probe",
        json={"probe_type": "liveness", "fail": True},
        headers={"X-Titan-Fault-Auth": "wrong-token"}
    )
    assert res_bad.status_code == 401


def test_simulated_error_surge_and_recovery(client: TestClient):
    auth_headers = {"X-Titan-Fault-Auth": "test-token-xyz"}

    # Enable 100% error surge
    surge_res = client.post(
        "/test/faults/error-surge",
        json={"enabled": True, "percentage": 100},
        headers=auth_headers
    )
    assert surge_res.status_code == 200

    # Normal requests should now receive simulated HTTP 500
    res_failed = client.get("/items")
    assert res_failed.status_code == 500
    assert res_failed.json()["error"] == "SimulatedInternalError"

    # Reset faults
    reset_res = client.post("/test/faults/reset", headers=auth_headers)
    assert reset_res.status_code == 200

    # Normal requests should succeed again
    res_recovered = client.get("/items")
    assert res_recovered.status_code == 200
