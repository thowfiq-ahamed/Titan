"""
TITAN Common Models & Domain Types
Shared schemas across Platform API, Incident Engine, and Reliability Lab.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ServiceTier(str, Enum):
    TIER_0 = "tier-0"  # Mission Critical
    TIER_1 = "tier-1"  # Core Business
    TIER_2 = "tier-2"  # Internal / Supporting


class DeploymentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class IncidentSeverity(str, Enum):
    P1_CRITICAL = "P1"
    P2_HIGH = "P2"
    P3_MEDIUM = "P3"
    P4_LOW = "P4"


class IncidentCategory(str, Enum):
    BAD_RELEASE = "bad_release"
    CONTAINER_CRASH = "container_crash"
    DEPENDENCY_OUTAGE = "dependency_outage"
    RESOURCE_PRESSURE = "resource_pressure"
    PROBE_FAILURE = "probe_failure"
    CONFIG_DRIFT = "config_drift"
    CONNECTIVITY_FAILURE = "connectivity_failure"
    UNKNOWN = "unknown"


class RecoveryStrategy(str, Enum):
    K8S_SELF_HEAL = "k8s_self_heal"
    APP_ROLLBACK = "app_rollback"
    GITOPS_RECONCILE = "gitops_reconcile"
    POLICY_RECOVERY = "policy_recovery"
    DIAGNOSIS_ONLY = "diagnosis_only"


class RecoveryStatus(str, Enum):
    RECOMMENDED = "recommended"
    APPROVED = "approved"
    EXECUTING = "executing"
    VERIFIED_SUCCESS = "verified_success"
    VERIFIED_FAILED = "verified_failed"
    REJECTED = "rejected"
