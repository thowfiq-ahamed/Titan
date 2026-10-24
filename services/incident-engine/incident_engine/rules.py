"""
TITAN Incident Engine - Deterministic Diagnosis Rules
Pure, auditable, explainable root-cause diagnosis without hallucinations.
"""

from typing import Any


class DiagnosisResult:
    def __init__(
        self,
        category: str,
        suspected_cause: str,
        confidence_score: float,
        supporting_evidence: list[dict[str, Any]],
        contradictory_evidence: list[dict[str, Any]],
        recommended_recovery: str,
        action_permitted: bool = True
    ):
        self.category = category
        self.suspected_cause = suspected_cause
        self.confidence_score = confidence_score
        self.supporting_evidence = supporting_evidence
        self.contradictory_evidence = contradictory_evidence
        self.recommended_recovery = recommended_recovery
        self.action_permitted = action_permitted

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "suspected_cause": self.suspected_cause,
            "confidence_score": self.confidence_score,
            "supporting_evidence": self.supporting_evidence,
            "contradictory_evidence": self.contradictory_evidence,
            "recommended_recovery": self.recommended_recovery,
            "action_permitted": self.action_permitted
        }


def diagnose_incident(
    alert_name: str,
    alert_category: str,
    annotations: dict[str, str],
    service_health: dict[str, Any],
    recent_deployment: dict[str, Any] | None = None
) -> DiagnosisResult:
    """
    Evaluates observed telemetry and alerts against deterministic root-cause rules.
    """
    supporting = []
    contradictory = []

    # Rule 1: Bad Application Release
    if alert_name == "TitanHighErrorRate" or alert_category == "bad_release":
        supporting.append({
            "source": "alertmanager",
            "signal": "TitanHighErrorRate",
            "detail": annotations.get("description", "High 5xx error rate detected")
        })
        if recent_deployment:
            supporting.append({
                "source": "deployments",
                "signal": "recent_image_rollout",
                "detail": f"New image tag '{recent_deployment.get('image_tag')}' was deployed recently"
            })
            confidence = 0.98
        else:
            contradictory.append({
                "source": "deployments",
                "signal": "no_recent_deployment",
                "detail": "No image release recorded in the last 15 minutes"
            })
            confidence = 0.85

        return DiagnosisResult(
            category="bad_release",
            suspected_cause="Defective release code throwing internal server errors (HTTP 500 surge)",
            confidence_score=confidence,
            supporting_evidence=supporting,
            contradictory_evidence=contradictory,
            recommended_recovery="app_rollback",
            action_permitted=True
        )

    # Rule 2: Database Dependency Outage
    if alert_name == "TitanDatabaseErrors" or alert_category == "dependency_outage":
        db_details = service_health.get("details", {}).get("database", {})
        supporting.append({
            "source": "health_probe",
            "signal": "readiness_probe_failing",
            "detail": db_details.get("message", "Database connection unhealthy")
        })
        is_live = service_health.get("status") == "alive"
        if is_live:
            supporting.append({
                "source": "process_runtime",
                "signal": "liveness_probe_alive",
                "detail": "Application container is running and responsive, confirming network/DB isolation rather than process crash"
            })

        return DiagnosisResult(
            category="dependency_outage",
            suspected_cause="PostgreSQL database unreachable or connection pool exhausted",
            confidence_score=0.94,
            supporting_evidence=supporting,
            contradictory_evidence=contradictory,
            recommended_recovery="policy_recovery",
            action_permitted=True
        )

    # Rule 3: Process Crash / Container Down
    if alert_name == "TitanWorkloadDown" or alert_category == "container_crash":
        supporting.append({
            "source": "prometheus",
            "signal": "up == 0",
            "detail": "Prometheus cannot scrape endpoint; process unreachable"
        })
        return DiagnosisResult(
            category="container_crash",
            suspected_cause="Container crashed, OOMKilled, or failed startup probe",
            confidence_score=0.91,
            supporting_evidence=supporting,
            contradictory_evidence=contradictory,
            recommended_recovery="k8s_self_heal",
            action_permitted=True
        )

    # Fallback / Unknown Category
    supporting.append({"source": "alertmanager", "signal": alert_name, "detail": str(annotations)})
    return DiagnosisResult(
        category="unknown",
        suspected_cause=f"Unclassified incident triggered by alert '{alert_name}'",
        confidence_score=0.60,
        supporting_evidence=supporting,
        contradictory_evidence=contradictory,
        recommended_recovery="diagnosis_only",
        action_permitted=False
    )
