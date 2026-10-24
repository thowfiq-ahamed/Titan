"""
TITAN Platform API - Deployment Tracking Endpoints
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_platform_db, DeploymentModel
from ..auth import require_api_key

router = APIRouter(prefix="/api/v1/deployments", tags=["Deployments"])


class DeploymentCreateDTO(BaseModel):
    service_id: str
    environment: str
    image_tag: str
    commit_sha: str
    desired_replicas: int = 2


class DeploymentUpdateDTO(BaseModel):
    status: Optional[str] = None
    gitops_synced: Optional[bool] = None
    healthy_replicas: Optional[int] = None


class DeploymentResponseDTO(BaseModel):
    id: str
    service_id: str
    environment: str
    image_tag: str
    commit_sha: str
    status: str
    gitops_synced: bool
    healthy_replicas: int
    desired_replicas: int
    started_at: str
    completed_at: Optional[str] = None


@router.get("", response_model=List[DeploymentResponseDTO])
def list_deployments(
    service_id: Optional[str] = None,
    environment: Optional[str] = None,
    db: Session = Depends(get_platform_db)
):
    query = select(DeploymentModel)
    if service_id:
        query = query.where(DeploymentModel.service_id == service_id)
    if environment:
        query = query.where(DeploymentModel.environment == environment)

    deps = db.scalars(query.order_by(DeploymentModel.started_at.desc())).all()
    return [
        DeploymentResponseDTO(
            id=d.id,
            service_id=d.service_id,
            environment=d.environment,
            image_tag=d.image_tag,
            commit_sha=d.commit_sha,
            status=d.status,
            gitops_synced=d.gitops_synced,
            healthy_replicas=d.healthy_replicas,
            desired_replicas=d.desired_replicas,
            started_at=d.started_at.isoformat(),
            completed_at=d.completed_at.isoformat() if d.completed_at else None
        )
        for d in deps
    ]


@router.post("", response_model=DeploymentResponseDTO, status_code=status.HTTP_201_CREATED)
def trigger_deployment(
    payload: DeploymentCreateDTO,
    db: Session = Depends(get_platform_db),
    _: str = Depends(require_api_key)
):
    dep = DeploymentModel(
        service_id=payload.service_id,
        environment=payload.environment,
        image_tag=payload.image_tag,
        commit_sha=payload.commit_sha,
        desired_replicas=payload.desired_replicas,
        status="in_progress",
        gitops_synced=False,
        healthy_replicas=0
    )
    db.add(dep)
    db.commit()
    db.refresh(dep)
    return DeploymentResponseDTO(
        id=dep.id,
        service_id=dep.service_id,
        environment=dep.environment,
        image_tag=dep.image_tag,
        commit_sha=dep.commit_sha,
        status=dep.status,
        gitops_synced=dep.gitops_synced,
        healthy_replicas=dep.healthy_replicas,
        desired_replicas=dep.desired_replicas,
        started_at=dep.started_at.isoformat(),
        completed_at=None
    )


@router.put("/{deployment_id}", response_model=DeploymentResponseDTO)
def update_deployment_status(
    deployment_id: str,
    payload: DeploymentUpdateDTO,
    db: Session = Depends(get_platform_db),
    _: str = Depends(require_api_key)
):
    dep = db.scalar(select(DeploymentModel).where(DeploymentModel.id == deployment_id))
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found.")

    if payload.status:
        dep.status = payload.status
        if payload.status in ("healthy", "failed", "rolled_back"):
            dep.completed_at = datetime.now(timezone.utc)
    if payload.gitops_synced is not None:
        dep.gitops_synced = payload.gitops_synced
    if payload.healthy_replicas is not None:
        dep.healthy_replicas = payload.healthy_replicas

    db.commit()
    db.refresh(dep)
    return DeploymentResponseDTO(
        id=dep.id,
        service_id=dep.service_id,
        environment=dep.environment,
        image_tag=dep.image_tag,
        commit_sha=dep.commit_sha,
        status=dep.status,
        gitops_synced=dep.gitops_synced,
        healthy_replicas=dep.healthy_replicas,
        desired_replicas=dep.desired_replicas,
        started_at=dep.started_at.isoformat(),
        completed_at=dep.completed_at.isoformat() if dep.completed_at else None
    )
