"""
TITAN Reliability Lab - Experiment Execution Engine
Runs automated reliability trials and computes empirical resilience benchmarks.
"""

import json
import time
import urllib.request
from datetime import UTC, datetime
from typing import Any

from .scenarios.base import BaseScenario
from .strategies.base import BaseRecoveryStrategy


class ExperimentRunner:
    def __init__(self, platform_api_url: str | None = "http://localhost:8000", api_key: str = "titan-platform-master-key-2026"):
        self.platform_api_url = platform_api_url
        self.api_key = api_key

    def run_trial(
        self,
        scenario: BaseScenario,
        strategy: BaseRecoveryStrategy,
        max_wait_seconds: int = 15
    ) -> dict[str, Any]:
        """
        Executes a single end-to-end reliability experiment trial:
        Precondition -> Fault -> Detection (MTTD) -> Diagnosis -> Recovery -> Verification (MTTR) -> Cleanup
        """
        trial_record = {
            "scenario_id": scenario.scenario_id,
            "title": scenario.name,
            "target_service": scenario.target_service,
            "target_environment": scenario.target_environment,
            "recovery_strategy": strategy.name,
            "preconditions_passed": False,
            "fault_injected": False,
            "detected": False,
            "diagnosed": False,
            "recovery_executed": False,
            "recovery_verified": False,
            "mttd_seconds": 0.0,
            "diagnosis_time_seconds": 0.0,
            "mttr_seconds": 0.0,
            "error": None
        }

        try:
            # 1. Precondition Check
            if not scenario.validate_preconditions():
                trial_record["error"] = "Precondition check failed: service not in healthy baseline"
                return trial_record
            trial_record["preconditions_passed"] = True

            # 2. Inject Fault
            scenario.inject_fault()
            trial_record["fault_injected"] = True

            # 3. Poll for Detection Signal (MTTD)
            start_poll = time.time()
            detected = False
            while (time.time() - start_poll) < max_wait_seconds:
                if scenario.check_detection_signal():
                    detected = True
                    break
                time.sleep(0.5)

            if not detected:
                trial_record["error"] = "Detection timeout: failure was not detected within threshold"
                return trial_record

            trial_record["detected"] = True
            scenario.diagnosed_at = datetime.now(UTC)
            trial_record["diagnosed"] = True

            # 4. Execute Recovery Strategy
            strategy.execute(scenario)
            trial_record["recovery_executed"] = True

            # 5. Verify Recovery (MTTR)
            start_verify = time.time()
            verified = False
            while (time.time() - start_verify) < max_wait_seconds:
                if scenario.verify_recovery():
                    verified = True
                    break
                time.sleep(0.5)

            trial_record["recovery_verified"] = verified
            metrics = scenario.get_metrics()
            trial_record["mttd_seconds"] = metrics["mttd_seconds"]
            trial_record["diagnosis_time_seconds"] = metrics["diagnosis_time_seconds"]
            trial_record["mttr_seconds"] = metrics["mttr_seconds"]

            # 6. Post result to Platform API if available
            self._record_to_platform(trial_record)

            return trial_record

        finally:
            scenario.cleanup()

    def _record_to_platform(self, record: dict):
        if not self.platform_api_url:
            return
        payload = {
            "scenario_id": record["scenario_id"],
            "title": record["title"],
            "target_service": record["target_service"],
            "target_environment": record["target_environment"],
            "fault_type": record["scenario_id"],
            "status": "completed" if record["recovery_verified"] else "failed",
            "detection_time_sec": record["mttd_seconds"],
            "diagnosis_time_sec": record["diagnosis_time_seconds"],
            "recovery_time_sec": record["mttr_seconds"],
            "recovery_strategy_used": record["recovery_strategy"],
            "verified": record["recovery_verified"]
        }
        try:
            req = urllib.request.Request(
                f"{self.platform_api_url}/api/v1/experiments",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "X-Titan-API-Key": self.api_key
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3):
                pass
        except Exception:
            pass
