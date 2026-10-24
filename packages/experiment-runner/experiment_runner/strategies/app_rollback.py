"""
Strategy B: Application Rollback
Restores previously healthy application version or baseline state.
"""

from typing import Any

from .base import BaseRecoveryStrategy


class ApplicationRollbackStrategy(BaseRecoveryStrategy):
    def __init__(self):
        super().__init__(
            name="app_rollback",
            description="Reverts target application deployment to the last known healthy state"
        )

    def execute(self, scenario: Any) -> dict[str, Any]:
        # Reset fault to simulate rolling back to healthy container image
        scenario.cleanup()
        return {
            "status": "executed",
            "strategy": self.name,
            "action": "Rolled back image to previous healthy digest and cleared fault."
        }
