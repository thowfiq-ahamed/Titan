"""
TITAN Platform API - Reliability Lab Experiment Endpoints
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_platform_db, ExperimentModel
from ..auth import require_api_key

router = APIRouter(prefix="/api/v1/experiments", tags=["Reliability Experiments"])


class ExperimentRecordDTO(BaseModel):
    scenario_id: str
    title: str
    target_service: str = "inventory-api"
    target_environment: str = "titan-dev"
    fault_type: str
    status: str = "completed"
    detection_time_sec: float
    diagnosis_time_sec: float
    recovery_time_sec: float
    recovery_strategy_used: str = "k8s_self_heal"
    verified: bool = True


class ExperimentResponseDTO(ExperimentRecordDTO):
    id: str
    created_at: str


@router.get("", response_model=List[ExperimentResponseDTO])
def list_experiments(
    target_service: Optional[str] = None,
    scenario_id: Optional[str] = None,
    db: Session = Depends(get_platform_db)
):
    query = select(ExperimentModel)
    if target_service:
        query = query.where(ExperimentModel.target_service == target_service)
    if scenario_id:
        query = query.where(ExperimentModel.scenario_id == scenario_id)

    experiments = db.scalars(query.order_by(ExperimentModel.created_at.desc())).all()
    return [
        ExperimentResponseDTO(
            id=exp.id,
            scenario_id=exp.scenario_id,
            title=exp.title,
            target_service=exp.target_service,
            target_environment=exp.target_environment,
            fault_type=exp.fault_type,
            status=exp.status,
            detection_time_sec=exp.detection_time_sec,
            diagnosis_time_sec=exp.diagnosis_time_sec,
            recovery_time_sec=exp.recovery_time_sec,
            recovery_strategy_used=exp.recovery_strategy_used,
            verified=exp.verified,
            created_at=exp.created_at.isoformat()
        )
        for exp in experiments
    ]


@router.post("", response_model=ExperimentResponseDTO, status_code=status.HTTP_201_CREATED)
def record_experiment_run(
    payload: ExperimentRecordDTO,
    db: Session = Depends(get_platform_db),
    _: str = Depends(require_api_key)
):
    exp = ExperimentModel(
        scenario_id=payload.scenario_id,
        title=payload.title,
        target_service=payload.target_service,
        target_environment=payload.target_environment,
        fault_type=payload.fault_type,
        status=payload.status,
        detection_time_sec=payload.detection_time_sec,
        diagnosis_time_sec=payload.diagnosis_time_sec,
        recovery_time_sec=payload.recovery_time_sec,
        recovery_strategy_used=payload.recovery_strategy_used,
        verified=payload.verified
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)

    return ExperimentResponseDTO(
        id=exp.id,
        scenario_id=exp.scenario_id,
        title=exp.title,
        target_service=exp.target_service,
        target_environment=exp.target_environment,
        fault_type=exp.fault_type,
        status=exp.status,
        detection_time_sec=exp.detection_time_sec,
        diagnosis_time_sec=exp.diagnosis_time_sec,
        recovery_time_sec=exp.recovery_time_sec,
        recovery_strategy_used=exp.recovery_strategy_used,
        verified=exp.verified,
        created_at=exp.created_at.isoformat()
    )
