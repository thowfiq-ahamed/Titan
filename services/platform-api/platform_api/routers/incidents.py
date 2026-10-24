"""
TITAN Platform API - Incident & Diagnosis Management Endpoints
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_api_key
from ..database import IncidentModel, get_platform_db

router = APIRouter(prefix="/api/v1/incidents", tags=["Incidents"])


class IncidentCreateDTO(BaseModel):
    service_id: str
    environment: str
    severity: str = "P2"
    category: str = "bad_release"
    suspected_cause: str
    confidence_score: float = 0.95
    supporting_evidence: list[dict[str, Any]] = []
    contradictory_evidence: list[dict[str, Any]] = []
    recommended_recovery: str = "app_rollback"
    recovery_status: str = "recommended"
    actual_recovery_action: str | None = None
    verification_passed: bool | None = None


class IncidentResponseDTO(IncidentCreateDTO):
    id: str
    detected_at: str
    resolved_at: str | None = None


class IncidentResolveDTO(BaseModel):
    recovery_status: str
    actual_recovery_action: str
    verification_passed: bool


@router.get("", response_model=list[IncidentResponseDTO])
def list_incidents(
    service_id: str | None = None,
    environment: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_platform_db)
):
    query = select(IncidentModel)
    if service_id:
        query = query.where(IncidentModel.service_id == service_id)
    if environment:
        query = query.where(IncidentModel.environment == environment)
    if category:
        query = query.where(IncidentModel.category == category)

    incidents = db.scalars(query.order_by(IncidentModel.detected_at.desc())).all()
    return [
        IncidentResponseDTO(
            id=inc.id,
            service_id=inc.service_id,
            environment=inc.environment,
            severity=inc.severity,
            category=inc.category,
            suspected_cause=inc.suspected_cause,
            confidence_score=inc.confidence_score,
            supporting_evidence=inc.supporting_evidence or [],
            contradictory_evidence=inc.contradictory_evidence or [],
            recommended_recovery=inc.recommended_recovery,
            recovery_status=inc.recovery_status,
            actual_recovery_action=inc.actual_recovery_action,
            verification_passed=inc.verification_passed,
            detected_at=inc.detected_at.isoformat(),
            resolved_at=inc.resolved_at.isoformat() if inc.resolved_at else None
        )
        for inc in incidents
    ]


@router.post("", response_model=IncidentResponseDTO, status_code=status.HTTP_201_CREATED)
def record_incident(
    payload: IncidentCreateDTO,
    db: Session = Depends(get_platform_db),
    _: str = Depends(require_api_key)
):
    new_inc = IncidentModel(
        service_id=payload.service_id,
        environment=payload.environment,
        severity=payload.severity,
        category=payload.category,
        suspected_cause=payload.suspected_cause,
        confidence_score=payload.confidence_score,
        supporting_evidence=payload.supporting_evidence,
        contradictory_evidence=payload.contradictory_evidence,
        recommended_recovery=payload.recommended_recovery,
        recovery_status=payload.recovery_status,
        actual_recovery_action=payload.actual_recovery_action,
        verification_passed=payload.verification_passed
    )
    db.add(new_inc)
    db.commit()
    db.refresh(new_inc)

    return IncidentResponseDTO(
        id=new_inc.id,
        service_id=new_inc.service_id,
        environment=new_inc.environment,
        severity=new_inc.severity,
        category=new_inc.category,
        suspected_cause=new_inc.suspected_cause,
        confidence_score=new_inc.confidence_score,
        supporting_evidence=new_inc.supporting_evidence or [],
        contradictory_evidence=new_inc.contradictory_evidence or [],
        recommended_recovery=new_inc.recommended_recovery,
        recovery_status=new_inc.recovery_status,
        actual_recovery_action=new_inc.actual_recovery_action,
        verification_passed=new_inc.verification_passed,
        detected_at=new_inc.detected_at.isoformat(),
        resolved_at=None
    )


@router.post("/{incident_id}/resolve", response_model=IncidentResponseDTO)
def resolve_incident(
    incident_id: str,
    payload: IncidentResolveDTO,
    db: Session = Depends(get_platform_db),
    _: str = Depends(require_api_key)
):
    inc = db.scalar(select(IncidentModel).where(IncidentModel.id == incident_id))
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found.")

    inc.recovery_status = payload.recovery_status
    inc.actual_recovery_action = payload.actual_recovery_action
    inc.verification_passed = payload.verification_passed
    inc.resolved_at = datetime.now(UTC)

    db.commit()
    db.refresh(inc)
    return IncidentResponseDTO(
        id=inc.id,
        service_id=inc.service_id,
        environment=inc.environment,
        severity=inc.severity,
        category=inc.category,
        suspected_cause=inc.suspected_cause,
        confidence_score=inc.confidence_score,
        supporting_evidence=inc.supporting_evidence or [],
        contradictory_evidence=inc.contradictory_evidence or [],
        recommended_recovery=inc.recommended_recovery,
        recovery_status=inc.recovery_status,
        actual_recovery_action=inc.actual_recovery_action,
        verification_passed=inc.verification_passed,
        detected_at=inc.detected_at.isoformat(),
        resolved_at=inc.resolved_at.isoformat() if inc.resolved_at else None
    )
