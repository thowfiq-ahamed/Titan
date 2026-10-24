"""
TITAN Reliability Lab - Base Scenario Interface
Defines the lifecycle of a controlled reliability experiment.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import time


class BaseScenario(ABC):
    def __init__(
        self,
        scenario_id: str,
        name: str,
        description: str,
        target_service: str,
        target_environment: str = "dev",
        timeout_seconds: int = 60
    ):
        self.scenario_id = scenario_id
        self.name = name
        self.description = description
        self.target_service = target_service
        self.target_environment = target_environment
        self.timeout_seconds = timeout_seconds

        # Run Telemetry & Timing
        self.started_at: Optional[datetime] = None
        self.fault_injected_at: Optional[datetime] = None
        self.detected_at: Optional[datetime] = None
        self.diagnosed_at: Optional[datetime] = None
        self.recovered_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    @abstractmethod
    def validate_preconditions(self) -> bool:
        """Verify target service is running and currently healthy."""
        pass

    @abstractmethod
    def inject_fault(self) -> Dict[str, Any]:
        """Inject the controlled failure."""
        pass

    @abstractmethod
    def check_detection_signal(self) -> bool:
        """Polls observability signals to determine if failure was detected."""
        pass

    @abstractmethod
    def verify_recovery(self) -> bool:
        """Validates that application recovered to healthy baseline."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Guaranteed cleanup to prevent leaked test failures."""
        pass

    def get_metrics(self) -> Dict[str, Any]:
        mttd = (self.detected_at - self.fault_injected_at).total_seconds() if self.detected_at and self.fault_injected_at else 0.0
        diag_time = (self.diagnosed_at - self.detected_at).total_seconds() if self.diagnosed_at and self.detected_at else 0.0
        mttr = (self.recovered_at - self.detected_at).total_seconds() if self.recovered_at and self.detected_at else 0.0

        return {
            "scenario_id": self.scenario_id,
            "target_service": self.target_service,
            "target_environment": self.target_environment,
            "mttd_seconds": round(max(mttd, 0.0), 3),
            "diagnosis_time_seconds": round(max(diag_time, 0.0), 3),
            "mttr_seconds": round(max(mttr, 0.0), 3),
        }
