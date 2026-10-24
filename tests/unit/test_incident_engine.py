"""
Unit & API tests for TITAN Incident Engine
"""

from fastapi.testclient import TestClient
from services.incident_engine.incident_engine.rules import diagnose_incident
from services.incident_engine.incident_engine.main import app

client = TestClient(app)


def test_diagnose_bad_release():
    result = diagnose_incident(
        alert_name="TitanHighErrorRate",
        alert_category="bad_release",
        annotations={"description": "5xx error rate exceeded 5%"},
        service_health={"status": "alive"},
        recent_deployment={"image_tag": "v1.0.1-rc1"}
    )
    assert result.category == "bad_release"
    assert result.confidence_score == 0.98
    assert result.recommended_recovery == "app_rollback"
    assert len(result.supporting_evidence) >= 2


def test_diagnose_dependency_outage():
    result = diagnose_incident(
        alert_name="TitanDatabaseErrors",
        alert_category="dependency_outage",
        annotations={"description": "DB connection timeout"},
        service_health={"status": "alive", "details": {"database": {"healthy": False, "message": "Connection refused"}}},
        recent_deployment=None
    )
    assert result.category == "dependency_outage"
    assert "PostgreSQL" in result.suspected_cause
    assert result.confidence_score >= 0.90
    assert result.recommended_recovery == "policy_recovery"


def test_alertmanager_webhook_endpoint():
    payload = {
        "version": "4",
        "status": "firing",
        "receiver": "titan-incident-engine-webhook",
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "TitanHighErrorRate",
                    "category": "bad_release",
                    "service": "inventory-api",
                    "environment": "development"
                },
                "annotations": {
                    "summary": "High 5xx error rate",
                    "description": "500 surge detected"
                }
            }
        ]
    }
    res = client.post("/api/v1/alerts", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 1
    diag = data["results"][0]["diagnosis"]
    assert diag["category"] == "bad_release"
    assert diag["recommended_recovery"] == "app_rollback"
