"""
TITAN Platform API - Environment Configuration Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_platform_db, EnvironmentModel
from ..auth import require_api_key

router = APIRouter(prefix="/api/v1/environments", tags=["Environments"])


class EnvironmentCreateDTO(BaseModel):
    name: str
    cluster_name: str = "titan-local-cluster"
    namespace: str
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    replicas: int = 2
    gitops_branch: str = "main"
    auto_sync: bool = True


class EnvironmentResponseDTO(EnvironmentCreateDTO):
    id: str


@router.get("", response_model=List[EnvironmentResponseDTO])
def list_environments(db: Session = Depends(get_platform_db)):
    envs = db.scalars(select(EnvironmentModel)).all()
    return [
        EnvironmentResponseDTO(
            id=e.id,
            name=e.name,
            cluster_name=e.cluster_name,
            namespace=e.namespace,
            cpu_limit=e.cpu_limit,
            memory_limit=e.memory_limit,
            replicas=e.replicas,
            gitops_branch=e.gitops_branch,
            auto_sync=e.auto_sync
        )
        for e in envs
    ]


@router.post("", response_model=EnvironmentResponseDTO, status_code=status.HTTP_201_CREATED)
def create_environment(
    payload: EnvironmentCreateDTO,
    db: Session = Depends(get_platform_db),
    _: str = Depends(require_api_key)
):
    existing = db.scalar(select(EnvironmentModel).where(EnvironmentModel.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail=f"Environment '{payload.name}' already exists.")

    new_env = EnvironmentModel(
        name=payload.name,
        cluster_name=payload.cluster_name,
        namespace=payload.namespace,
        cpu_limit=payload.cpu_limit,
        memory_limit=payload.memory_limit,
        replicas=payload.replicas,
        gitops_branch=payload.gitops_branch,
        auto_sync=payload.auto_sync
    )
    db.add(new_env)
    db.commit()
    db.refresh(new_env)
    return EnvironmentResponseDTO(
        id=new_env.id,
        name=new_env.name,
        cluster_name=new_env.cluster_name,
        namespace=new_env.namespace,
        cpu_limit=new_env.cpu_limit,
        memory_limit=new_env.memory_limit,
        replicas=new_env.replicas,
        gitops_branch=new_env.gitops_branch,
        auto_sync=new_env.auto_sync
    )
