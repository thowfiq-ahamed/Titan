"""
TITAN Platform API - Service Catalog Endpoints
"""


from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_api_key
from ..database import ServiceModel, get_platform_db

router = APIRouter(prefix="/api/v1/services", tags=["Service Catalog"])


class ServiceCreateDTO(BaseModel):
    name: str
    display_name: str
    description: str | None = None
    owner_team: str = "platform-engineering"
    repo_url: str = "https://github.com/thowfiq-ahamed/Titan"
    tier: str = "tier-1"
    health_endpoint: str = "/health/ready"
    metrics_endpoint: str = "/metrics"


class ServiceResponseDTO(ServiceCreateDTO):
    id: str
    created_at: str
    updated_at: str


@router.get("", response_model=list[ServiceResponseDTO], summary="List registered services")
def list_services(db: Session = Depends(get_platform_db)):
    services = db.scalars(select(ServiceModel).order_by(ServiceModel.name)).all()
    return [
        ServiceResponseDTO(
            id=s.id,
            name=s.name,
            display_name=s.display_name,
            description=s.description,
            owner_team=s.owner_team,
            repo_url=s.repo_url,
            tier=s.tier,
            health_endpoint=s.health_endpoint,
            metrics_endpoint=s.metrics_endpoint,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat()
        )
        for s in services
    ]


@router.post("", response_model=ServiceResponseDTO, status_code=status.HTTP_201_CREATED, summary="Register new service")
def register_service(
    payload: ServiceCreateDTO,
    db: Session = Depends(get_platform_db),
    _: str = Depends(require_api_key)
):
    existing = db.scalar(select(ServiceModel).where(ServiceModel.name == payload.name))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Service '{payload.name}' is already registered."
        )

    new_service = ServiceModel(
        name=payload.name,
        display_name=payload.display_name,
        description=payload.description,
        owner_team=payload.owner_team,
        repo_url=payload.repo_url,
        tier=payload.tier,
        health_endpoint=payload.health_endpoint,
        metrics_endpoint=payload.metrics_endpoint
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return ServiceResponseDTO(
        id=new_service.id,
        name=new_service.name,
        display_name=new_service.display_name,
        description=new_service.description,
        owner_team=new_service.owner_team,
        repo_url=new_service.repo_url,
        tier=new_service.tier,
        health_endpoint=new_service.health_endpoint,
        metrics_endpoint=new_service.metrics_endpoint,
        created_at=new_service.created_at.isoformat(),
        updated_at=new_service.updated_at.isoformat()
    )


@router.get("/{service_id}", response_model=ServiceResponseDTO, summary="Get service by ID or name")
def get_service(service_id: str, db: Session = Depends(get_platform_db)):
    service = db.scalar(select(ServiceModel).where((ServiceModel.id == service_id) | (ServiceModel.name == service_id)))
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_id}' not found."
        )
    return ServiceResponseDTO(
        id=service.id,
        name=service.name,
        display_name=service.display_name,
        description=service.description,
        owner_team=service.owner_team,
        repo_url=service.repo_url,
        tier=service.tier,
        health_endpoint=service.health_endpoint,
        metrics_endpoint=service.metrics_endpoint,
        created_at=service.created_at.isoformat(),
        updated_at=service.updated_at.isoformat()
    )
