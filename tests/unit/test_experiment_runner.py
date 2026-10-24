"""
Unit tests for TITAN Reliability Lab Experiment Runner
"""

from unittest.mock import MagicMock
from datetime import datetime, timezone
from packages.experiment_runner.src.runner import ExperimentRunner
from packages.experiment_runner.src.scenarios.base import BaseScenario
from packages.experiment_runner.src.strategies.app_rollback import ApplicationRollbackStrategy
from packages.experiment_runner.src.strategies.policy_recovery import PolicyControlledRecoveryStrategy


class MockScenario(BaseScenario):
    def __init__(self):
        super().__init__(
            scenario_id="SCN-TEST",
            name="Mock Test Scenario",
            description="Testing runner lifecycle",
            target_service="test-service"
        )
        self.cleaned_up = False
        self.fault_active = False

    def validate_preconditions(self) -> bool:
        return True

    def inject_fault(self):
        self.fault_active = True
        self.fault_injected_at = datetime.now(timezone.utc)
        return {"status": "injected"}

    def check_detection_signal(self) -> bool:
        if self.fault_active:
            self.detected_at = datetime.now(timezone.utc)
            return True
        return False

    def verify_recovery(self) -> bool:
        if not self.fault_active:
            self.recovered_at = datetime.now(timezone.utc)
            return True
        return False

    def cleanup(self):
        self.fault_active = False
        self.cleaned_up = True
        self.completed_at = datetime.now(timezone.utc)


def test_experiment_runner_full_cycle():
    scenario = MockScenario()
    strategy = ApplicationRollbackStrategy()
    runner = ExperimentRunner(platform_api_url=None)  # No remote API during unit test

    result = runner.run_trial(scenario, strategy)

    assert result["preconditions_passed"] is True
    assert result["fault_injected"] is True
    assert result["detected"] is True
    assert result["diagnosed"] is True
    assert result["recovery_executed"] is True
    assert result["recovery_verified"] is True
    assert scenario.cleaned_up is True
    assert result["mttd_seconds"] >= 0.0
    assert result["mttr_seconds"] >= 0.0


def test_policy_controlled_recovery_strategy():
    scenario = MockScenario()
    strategy = PolicyControlledRecoveryStrategy(allowed_actions=["rollback_version"])
    res = strategy.execute(scenario)
    assert res["status"] == "executed"
    assert res["policy_checked"] is True


def test_policy_denial_for_unauthorized_action():
    scenario = MockScenario()
    strategy = PolicyControlledRecoveryStrategy(allowed_actions=["restart_only"])
    res = strategy.execute(scenario)
    assert res["status"] == "policy_denied"
