"""
TITAN Domain Schemas
Pydantic v2 domain schemas for platform operations.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .enums import (
    ServiceTier, DeploymentStatus, IncidentSeverity,
    IncidentCategory, RecoveryStrategy, RecoveryStatus
)


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=64, description="Service identifier (e.g. inventory-api)")
    display_name: str = Field(..., max_length=128)
    description: Optional[str] = None
    owner_team: str = Field(default="platform-engineering")
    repo_url: str = Field(default="https://github.com/titan-platform/titan")
    tier: ServiceTier = ServiceTier.TIER_1
    health_endpoint: str = Field(default="/health/ready")
    metrics_endpoint: str = Field(default="/metrics")


class ServiceCreate(ServiceBase):
    pass


class ServiceResponse(ServiceBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime


class EnvironmentConfig(BaseModel):
    name: str = Field(..., description="dev, staging, or prod")
    cluster_name: str = Field(default="titan-local-cluster")
    namespace: str = Field(default="titan-dev")
    cpu_limit: str = Field(default="500m")
    memory_limit: str = Field(default="512Mi")
    replicas: int = Field(default=2, ge=1)
    gitops_branch: str = Field(default="main")
    auto_sync: bool = Field(default=True)


class DeploymentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    service_id: str
    environment: str
    image_tag: str
    commit_sha: str
    status: DeploymentStatus
    gitops_synced: bool
    healthy_replicas: int
    desired_replicas: int
    started_at: datetime
    completed_at: Optional[datetime] = None


class DiagnosticEvidence(BaseModel):
    source: str = Field(..., description="metrics, logs, k8s_events, alertmanager")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signal_name: str
    observed_value: Any
    threshold: Optional[Any] = None
    detail: str


class IncidentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    service_id: str
    environment: str
    severity: IncidentSeverity
    category: IncidentCategory
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    suspected_cause: str
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    contradictory_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_recovery: RecoveryStrategy
    recovery_status: RecoveryStatus
    actual_recovery_action: Optional[str] = None
    verification_passed: Optional[bool] = None


class ExperimentDefinition(BaseModel):
    scenario_id: str
    title: str
    description: str
    target_service: str
    target_environment: str
    fault_type: str
    fault_parameters: Dict[str, Any] = Field(default_factory=dict)
    expected_signal: str
    allowed_recovery_strategies: List[RecoveryStrategy]
    max_duration_seconds: int = 120
    cleanup_procedure: str


class BenchmarkSummary(BaseModel):
    total_experiments: int
    successful_recoveries: int
    failed_recoveries: int
    recovery_success_rate_pct: float
    mean_time_to_detect_seconds: float
    mean_time_to_diagnose_seconds: float
    mean_time_to_recover_seconds: float
    diagnosis_accuracy_pct: float
    gitops_state_consistency_pct: float
