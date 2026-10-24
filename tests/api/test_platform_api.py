"""
API tests for TITAN Platform API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from platform_api.main import app as platform_app
from platform_api.database import Base as PlatformBase, get_platform_db

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="module")
def platform_client():
    PlatformBase.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    platform_app.dependency_overrides[get_platform_db] = override_get_db
    with TestClient(platform_app) as client:
        yield client
    platform_app.dependency_overrides.clear()
    PlatformBase.metadata.drop_all(bind=test_engine)


AUTH_HEADER = {"X-Titan-API-Key": "titan-platform-master-key-2026"}


def test_platform_health(platform_client: TestClient):
    res = platform_client.get("/health/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"


def test_service_registration_and_list(platform_client: TestClient):
    payload = {
        "name": "payment-api",
        "display_name": "Payment Gateway Service",
        "owner_team": "checkout-squad",
        "tier": "tier-0",
        "health_endpoint": "/healthz",
        "metrics_endpoint": "/metrics"
    }
    # 1. Register service
    res = platform_client.post("/api/v1/services", json=payload, headers=AUTH_HEADER)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "payment-api"
    assert data["tier"] == "tier-0"

    # 2. Duplicate registration conflict
    res_dup = platform_client.post("/api/v1/services", json=payload, headers=AUTH_HEADER)
    assert res_dup.status_code == 409

    # 3. List services
    res_list = platform_client.get("/api/v1/services")
    assert res_list.status_code == 200
    names = [s["name"] for s in res_list.json()]
    assert "payment-api" in names


def test_environment_configuration(platform_client: TestClient):
    payload = {
        "name": "sandbox",
        "cluster_name": "titan-sandbox-eks",
        "namespace": "titan-sandbox",
        "cpu_limit": "250m",
        "memory_limit": "256Mi",
        "replicas": 1
    }
    res = platform_client.post("/api/v1/environments", json=payload, headers=AUTH_HEADER)
    assert res.status_code == 201
    assert res.json()["namespace"] == "titan-sandbox"


def test_incident_lifecycle(platform_client: TestClient):
    # Record incident
    inc_payload = {
        "service_id": "payment-api",
        "environment": "sandbox",
        "severity": "P1",
        "category": "bad_release",
        "suspected_cause": "OOMKill surge following memory leak in v2.1.0",
        "confidence_score": 0.98,
        "supporting_evidence": [{"source": "k8s_events", "signal_name": "OOMKilled", "observed_value": 5}],
        "recommended_recovery": "app_rollback"
    }
    res = platform_client.post("/api/v1/incidents", json=inc_payload, headers=AUTH_HEADER)
    assert res.status_code == 201
    inc_id = res.json()["id"]

    # Resolve incident
    resolve_payload = {
        "recovery_status": "verified_success",
        "actual_recovery_action": "Rolled back deployment to image tag v2.0.9",
        "verification_passed": True
    }
    res_resolve = platform_client.post(f"/api/v1/incidents/{inc_id}/resolve", json=resolve_payload, headers=AUTH_HEADER)
    assert res_resolve.status_code == 200
    assert res_resolve.json()["verification_passed"] is True
    assert res_resolve.json()["resolved_at"] is not None


def test_experiment_and_benchmark_calculation(platform_client: TestClient):
    # Record two experiment trials
    exp1 = {
        "scenario_id": "SCN-001",
        "title": "Broken Release 500 Surge",
        "target_service": "inventory-api",
        "target_environment": "dev",
        "fault_type": "error_surge",
        "detection_time_sec": 4.2,
        "diagnosis_time_sec": 2.1,
        "recovery_time_sec": 12.5,
        "recovery_strategy_used": "app_rollback",
        "verified": True
    }
    exp2 = {
        "scenario_id": "SCN-002",
        "title": "Probe Deadlock",
        "target_service": "inventory-api",
        "target_environment": "dev",
        "fault_type": "probe_failure",
        "detection_time_sec": 6.8,
        "diagnosis_time_sec": 3.4,
        "recovery_time_sec": 18.0,
        "recovery_strategy_used": "k8s_self_heal",
        "verified": True
    }
    platform_client.post("/api/v1/experiments", json=exp1, headers=AUTH_HEADER)
    platform_client.post("/api/v1/experiments", json=exp2, headers=AUTH_HEADER)

    # Fetch benchmark summary
    res = platform_client.get("/api/v1/benchmarks/summary")
    assert res.status_code == 200
    bm = res.json()
    assert bm["total_experiments"] >= 2
    assert bm["recovery_success_rate_pct"] == 100.0
    assert bm["mean_time_to_detect_seconds"] > 0
    assert "app_rollback" in bm["strategy_breakdown"]
    assert "k8s_self_heal" in bm["strategy_breakdown"]
