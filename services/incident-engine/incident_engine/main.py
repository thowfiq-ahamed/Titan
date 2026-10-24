"""
TITAN Incident Engine - Main Service
Ingests Prometheus Alertmanager webhooks, performs deterministic RCA,
and coordinates policy-controlled recovery.
"""

import json
import urllib.request
from typing import Any

from fastapi import FastAPI, Header
from pydantic import BaseModel

from .config import settings
from .rules import diagnose_incident

app = FastAPI(
    title="TITAN Incident Engine",
    description="Deterministic RCA & Resilience Intelligence Service",
    version=settings.APP_VERSION
)


class AlertItem(BaseModel):
    status: str
    labels: dict[str, str] = {}
    annotations: dict[str, str] = {}
    startsAt: str | None = None
    endsAt: str | None = None


class AlertmanagerWebhookPayload(BaseModel):
    version: str = "4"
    groupKey: str = ""
    status: str = "firing"
    receiver: str = "titan-incident-engine-webhook"
    alerts: list[AlertItem] = []


def record_to_platform_api(diagnosis_data: dict[str, Any], service_id: str, env: str) -> str | None:
    """Posts the diagnosed incident to the central TITAN Platform API."""
    if not settings.PLATFORM_API_URL:
        return None
    payload = {
        "service_id": service_id,
        "environment": env,
        "severity": "P1" if diagnosis_data["category"] in ("bad_release", "container_crash") else "P2",
        "category": diagnosis_data["category"],
        "suspected_cause": diagnosis_data["suspected_cause"],
        "confidence_score": diagnosis_data["confidence_score"],
        "supporting_evidence": diagnosis_data["supporting_evidence"],
        "contradictory_evidence": diagnosis_data["contradictory_evidence"],
        "recommended_recovery": diagnosis_data["recommended_recovery"],
        "recovery_status": "approved" if settings.DIAGNOSIS_MODE == "remediation" else "recommended",
        "actual_recovery_action": None,
        "verification_passed": None
    }
    try:
        req = urllib.request.Request(
            f"{settings.PLATFORM_API_URL}/api/v1/incidents",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Titan-API-Key": settings.PLATFORM_API_KEY
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            res_body = json.loads(res.read().decode("utf-8"))
            return res_body.get("id")
    except Exception:
        return None


@app.get("/health/ready")
def get_readiness():
    return {
        "status": "ready",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "diagnosis_mode": settings.DIAGNOSIS_MODE
    }


@app.post("/api/v1/alerts")
def receive_alertmanager_webhook(
    payload: AlertmanagerWebhookPayload,
    authorization: str | None = Header(None)
):
    """
    Webhook handler for Alertmanager notifications.
    Processes each firing alert, executes deterministic diagnosis, and records evidence.
    """
    processed = []
    for alert in payload.alerts:
        if alert.status != "firing":
            continue

        alert_name = alert.labels.get("alertname", "UnknownAlert")
        category = alert.labels.get("category", "unknown")
        service_id = alert.labels.get("service", "inventory-api")
        env = alert.labels.get("environment", "development")

        # Mock current health snapshot or fetch live
        health_snapshot = {"status": "alive", "details": {"database": {"healthy": True}}}
        if category == "dependency_outage":
            health_snapshot["details"]["database"]["healthy"] = False

        # Run diagnosis
        diagnosis = diagnose_incident(
            alert_name=alert_name,
            alert_category=category,
            annotations=alert.annotations,
            service_health=health_snapshot,
            recent_deployment={"image_tag": "v1.0.1-rc1"} if category == "bad_release" else None
        )

        incident_id = record_to_platform_api(diagnosis.to_dict(), service_id, env)
        processed.append({
            "alert": alert_name,
            "incident_id": incident_id,
            "diagnosis": diagnosis.to_dict()
        })

    return {
        "status": "processed",
        "count": len(processed),
        "results": processed
    }
