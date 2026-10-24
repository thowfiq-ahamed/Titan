"""
TITAN Platform API - Database Engine and Models
"""

import uuid
from collections.abc import Generator
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings


class Base(DeclarativeBase):
    pass


# 1. Service Model
class ServiceModel(Base):
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_team: Mapped[str] = mapped_column(String(64), default="platform-engineering")
    repo_url: Mapped[str] = mapped_column(String(255), default="https://github.com/thowfiq-ahamed/Titan")
    tier: Mapped[str] = mapped_column(String(16), default="tier-1")
    health_endpoint: Mapped[str] = mapped_column(String(128), default="/health/ready")
    metrics_endpoint: Mapped[str] = mapped_column(String(128), default="/metrics")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


# 2. Environment Model
class EnvironmentModel(Base):
    __tablename__ = "environments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    cluster_name: Mapped[str] = mapped_column(String(64), default="titan-local-cluster")
    namespace: Mapped[str] = mapped_column(String(64), nullable=False)
    cpu_limit: Mapped[str] = mapped_column(String(16), default="500m")
    memory_limit: Mapped[str] = mapped_column(String(16), default="512Mi")
    replicas: Mapped[int] = mapped_column(Integer, default=2)
    gitops_branch: Mapped[str] = mapped_column(String(64), default="main")
    auto_sync: Mapped[bool] = mapped_column(Boolean, default=True)


# 3. Deployment Model
class DeploymentModel(Base):
    __tablename__ = "deployments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    environment: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    image_tag: Mapped[str] = mapped_column(String(128), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    gitops_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    healthy_replicas: Mapped[int] = mapped_column(Integer, default=0)
    desired_replicas: Mapped[int] = mapped_column(Integer, default=2)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# 4. Incident Model
class IncidentModel(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    environment: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(8), default="P2")
    category: Mapped[str] = mapped_column(String(64), default="unknown")
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspected_cause: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.95)
    supporting_evidence: Mapped[list] = mapped_column(JSON, default=list)
    contradictory_evidence: Mapped[list] = mapped_column(JSON, default=list)
    recommended_recovery: Mapped[str] = mapped_column(String(64), default="diagnosis_only")
    recovery_status: Mapped[str] = mapped_column(String(32), default="recommended")
    actual_recovery_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)


# 5. Experiment Run Model
class ExperimentModel(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_service: Mapped[str] = mapped_column(String(64), nullable=False)
    target_environment: Mapped[str] = mapped_column(String(32), nullable=False)
    fault_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="completed")  # running, completed, failed
    detection_time_sec: Mapped[float] = mapped_column(Float, default=0.0)
    diagnosis_time_sec: Mapped[float] = mapped_column(Float, default=0.0)
    recovery_time_sec: Mapped[float] = mapped_column(Float, default=0.0)
    recovery_strategy_used: Mapped[str] = mapped_column(String(64), default="k8s_self_heal")
    verified: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# Engine setup
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine_kwargs = {}
if is_sqlite:
    if ":memory:" in settings.DATABASE_URL:
        engine_kwargs["poolclass"] = StaticPool
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_platform_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_platform_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
