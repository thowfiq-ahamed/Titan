"""
TITAN Inventory API - Health Probes
Implements Kubernetes-compatible liveness and readiness probes.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from ..config import settings
from ..database import check_database_health
from ..metrics import DATABASE_ERRORS_TOTAL

router = APIRouter(prefix="/health", tags=["Health"])

# Global state for controlled simulated probe failures (used by Reliability Lab)
_simulated_faults = {
    "liveness_failure": False,
    "readiness_failure": False,
}


def set_simulated_probe_fault(probe_type: str, enabled: bool) -> None:
    if probe_type in _simulated_faults:
        _simulated_faults[probe_type] = enabled


def get_simulated_probe_faults() -> dict:
    return _simulated_faults.copy()


class HealthStatus(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    environment: str
    details: dict | None = None


@router.get(
    "/live",
    response_model=HealthStatus,
    summary="Liveness Probe",
    description="Kubernetes liveness probe. Indicates if the process is running and not deadlocked."
)
def get_liveness(response: Response) -> HealthStatus:
    if _simulated_faults["liveness_failure"]:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return HealthStatus(
            status="unhealthy",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            timestamp=datetime.now(timezone.utc).isoformat(),
            environment=settings.ENVIRONMENT,
            details={"error": "Simulated liveness deadlock active"}
        )

    return HealthStatus(
        status="alive",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT
    )


@router.get(
    "/ready",
    response_model=HealthStatus,
    summary="Readiness Probe",
    description="Kubernetes readiness probe. Checks if the service and database dependencies are ready for traffic."
)
def get_readiness(response: Response) -> HealthStatus:
    # Check simulated readiness fault
    if _simulated_faults["readiness_failure"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthStatus(
            status="not_ready",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            timestamp=datetime.now(timezone.utc).isoformat(),
            environment=settings.ENVIRONMENT,
            details={"dependency": "readiness_simulation", "error": "Simulated readiness probe failure active"}
        )

    # Perform real database readiness check
    db_healthy, latency_ms, msg = check_database_health()
    if not db_healthy:
        DATABASE_ERRORS_TOTAL.labels(operation="readiness_probe").inc()
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthStatus(
            status="not_ready",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            timestamp=datetime.now(timezone.utc).isoformat(),
            environment=settings.ENVIRONMENT,
            details={"database": {"healthy": False, "latency_ms": latency_ms, "message": msg}}
        )

    return HealthStatus(
        status="ready",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT,
        details={"database": {"healthy": True, "latency_ms": latency_ms}}
    )
