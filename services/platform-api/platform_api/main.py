"""
TITAN Platform API - Main Application
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .config import settings
from .database import EnvironmentModel, ServiceModel, SessionLocal, init_platform_db
from .routers import benchmarks, deployments, environments, experiments, health, incidents, services


def seed_defaults():
    """Seeds default inventory-api service and standard environments if empty."""
    db = SessionLocal()
    try:
        if not db.scalar(select(ServiceModel).where(ServiceModel.name == "inventory-api")):
            db.add(ServiceModel(
                name="inventory-api",
                display_name="Enterprise Inventory API",
                description="Core inventory and asset management microservice",
                owner_team="platform-engineering",
                repo_url="https://github.com/thowfiq-ahamed/Titan",
                tier="tier-1",
                health_endpoint="/health/ready",
                metrics_endpoint="/metrics"
            ))

        for env_name, ns in [("dev", "titan-dev"), ("staging", "titan-staging"), ("prod", "titan-prod")]:
            if not db.scalar(select(EnvironmentModel).where(EnvironmentModel.name == env_name)):
                db.add(EnvironmentModel(
                    name=env_name,
                    cluster_name="titan-k8s-cluster",
                    namespace=ns,
                    cpu_limit="500m" if env_name != "prod" else "1000m",
                    memory_limit="512Mi" if env_name != "prod" else "1024Mi",
                    replicas=2 if env_name != "prod" else 4,
                    gitops_branch=env_name if env_name != "prod" else "main",
                    auto_sync=True
                ))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_platform_db()
    seed_defaults()
    yield


app = FastAPI(
    title="TITAN Platform API",
    description="Central Platform Engineering Control Plane & Reliability Intelligence API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(services.router)
app.include_router(environments.router)
app.include_router(deployments.router)
app.include_router(incidents.router)
app.include_router(experiments.router)
app.include_router(benchmarks.router)


@app.get("/")
def platform_root():
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs"
    }
