"""
TITAN Inventory API - Controlled Test-Only Fault Injection Router
Used strictly by TITAN Reliability Lab for empirical resilience benchmarking.
Guarded by security flags and auth tokens. NEVER enabled in production.
"""

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from ..config import settings
from ..logging import logger
from ..metrics import SIMULATED_FAULTS_TOTAL
from .health import get_simulated_probe_faults, set_simulated_probe_fault

router = APIRouter(prefix="/test/faults", tags=["Reliability Lab Fault Injection"])

# In-memory fault state
_fault_state: dict[str, Any] = {
    "error_rate_enabled": False,
    "error_rate_percentage": 0,
    "artificial_latency_ms": 0,
    "database_outage_simulated": False,
}


def verify_fault_injection_authorized(
    x_titan_fault_auth: str = Header(..., alias="X-Titan-Fault-Auth")
) -> bool:
    """Security gate ensuring fault injection is explicitly enabled and authenticated."""
    if not settings.ENABLE_FAULT_INJECTION:
        logger.warning("Attempted fault injection when ENABLE_FAULT_INJECTION is disabled.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Controlled fault injection is strictly disabled in this environment."
        )

    if not settings.FAULT_INJECTION_AUTH_TOKEN or x_titan_fault_auth != settings.FAULT_INJECTION_AUTH_TOKEN:
        logger.warning("Unauthorized fault injection attempt with invalid or unconfigured token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid fault injection authorization token."
        )
    return True


class ProbeFaultRequest(BaseModel):
    probe_type: str = Field(..., description="'liveness' or 'readiness'")
    fail: bool = Field(..., description="True to simulate failure, False to restore")


class LatencyFaultRequest(BaseModel):
    latency_ms: int = Field(..., ge=0, le=30000, description="Milliseconds of artificial latency")


class ErrorSurgeFaultRequest(BaseModel):
    enabled: bool = Field(...)
    percentage: int = Field(default=100, ge=0, le=100, description="Percentage of requests to fail with 500")


class DbOutageFaultRequest(BaseModel):
    simulate_outage: bool = Field(..., description="True to disconnect DB access, False to restore")


@router.get(
    "/status",
    summary="Get Active Fault State",
    dependencies=[Depends(verify_fault_injection_authorized)]
)
def get_fault_status() -> dict[str, Any]:
    probes = get_simulated_probe_faults()
    return {
        "fault_injection_enabled": settings.ENABLE_FAULT_INJECTION,
        "environment": settings.ENVIRONMENT,
        "probe_faults": probes,
        "runtime_faults": _fault_state,
    }


@router.post(
    "/probe",
    summary="Simulate Kubernetes Probe Failure",
    dependencies=[Depends(verify_fault_injection_authorized)]
)
def inject_probe_fault(payload: ProbeFaultRequest) -> dict[str, Any]:
    probe_key = f"{payload.probe_type.lower()}_failure"
    set_simulated_probe_fault(probe_key, payload.fail)
    action = "injected" if payload.fail else "cleared"
    SIMULATED_FAULTS_TOTAL.labels(fault_type=f"probe_{payload.probe_type}_{action}").inc()
    logger.info(f"Reliability Lab: {action} simulated probe fault for {payload.probe_type}")
    return {"status": "success", "probe_type": payload.probe_type, "failed": payload.fail}


@router.post(
    "/latency",
    summary="Simulate Service Latency",
    dependencies=[Depends(verify_fault_injection_authorized)]
)
def inject_latency_fault(payload: LatencyFaultRequest) -> dict[str, Any]:
    _fault_state["artificial_latency_ms"] = payload.latency_ms
    SIMULATED_FAULTS_TOTAL.labels(fault_type="latency").inc()
    logger.info(f"Reliability Lab: configured artificial latency of {payload.latency_ms}ms")
    return {"status": "success", "latency_ms": payload.latency_ms}


@router.post(
    "/error-surge",
    summary="Simulate HTTP 500 Error Surge (Bad Release)",
    dependencies=[Depends(verify_fault_injection_authorized)]
)
def inject_error_surge_fault(payload: ErrorSurgeFaultRequest) -> dict[str, Any]:
    _fault_state["error_rate_enabled"] = payload.enabled
    _fault_state["error_rate_percentage"] = payload.percentage
    SIMULATED_FAULTS_TOTAL.labels(fault_type="error_surge").inc()
    logger.info(f"Reliability Lab: configured error surge (enabled={payload.enabled}, rate={payload.percentage}%)")
    return {"status": "success", "error_surge": _fault_state["error_rate_enabled"], "rate": payload.percentage}


@router.post(
    "/reset",
    summary="Clear All Injected Faults",
    dependencies=[Depends(verify_fault_injection_authorized)]
)
def reset_all_faults() -> dict[str, Any]:
    set_simulated_probe_fault("liveness_failure", False)
    set_simulated_probe_fault("readiness_failure", False)
    _fault_state["error_rate_enabled"] = False
    _fault_state["error_rate_percentage"] = 0
    _fault_state["artificial_latency_ms"] = 0
    _fault_state["database_outage_simulated"] = False
    logger.info("Reliability Lab: cleared all simulated faults; normal state restored.")
    return {"status": "success", "message": "All simulated faults reset to healthy baseline."}


def get_runtime_fault_state() -> dict[str, Any]:
    return _fault_state
