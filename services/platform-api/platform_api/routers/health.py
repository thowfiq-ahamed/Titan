"""
TITAN Platform API - Health Probes
"""

from datetime import UTC, datetime

from fastapi import APIRouter

from ..config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
def get_liveness():
    return {
        "status": "alive",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(UTC).isoformat()
    }


@router.get("/ready")
def get_readiness():
    return {
        "status": "ready",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(UTC).isoformat()
    }
