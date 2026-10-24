"""
TITAN Reliability Lab - Recovery Strategy Base Interface
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseRecoveryStrategy(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, scenario: Any) -> dict[str, Any]:
        """Executes the recovery action on the target scenario."""
        pass
