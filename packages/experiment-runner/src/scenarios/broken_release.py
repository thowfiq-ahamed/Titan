"""
Scenario SCN-001: Broken Release HTTP Error Surge
Simulates deployment of a corrupted release throwing HTTP 500s.
"""

from typing import Dict, Any
from datetime import datetime, timezone
import urllib.request
import urllib.error
import json
from .base import BaseScenario


class BrokenReleaseScenario(BaseScenario):
    def __init__(self, target_url: str = "http://localhost:8001", auth_token: str = "dev-reliability-test-key-32ch"):
        super().__init__(
            scenario_id="SCN-001",
            name="Broken Release Error Surge",
            description="Simulates bad application release producing persistent HTTP 500 errors",
            target_service="inventory-api",
            target_environment="dev"
        )
        self.target_url = target_url
        self.auth_token = auth_token

    def _request(self, path: str, method: str = "GET", payload: dict = None, headers: dict = None) -> tuple[int, dict]:
        h = headers or {}
        data = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(f"{self.target_url}{path}", data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=3) as res:
                return res.status, json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                body = json.loads(exc.read().decode("utf-8"))
            except Exception:
                body = {}
            return exc.code, body
        except Exception:
            return 0, {}

    def validate_preconditions(self) -> bool:
        status, body = self._request("/health/ready")
        return status == 200 and body.get("status") == "ready"

    def inject_fault(self) -> Dict[str, Any]:
        self.fault_injected_at = datetime.now(timezone.utc)
        status, body = self._request(
            "/test/faults/error-surge",
            method="POST",
            payload={"enabled": True, "percentage": 100},
            headers={"Content-Type": "application/json", "X-Titan-Fault-Auth": self.auth_token}
        )
        return {"status_code": status, "payload": body}

    def check_detection_signal(self) -> bool:
        # Probe workload endpoint to observe failure
        status, _ = self._request("/items")
        if status == 500:
            self.detected_at = datetime.now(timezone.utc)
            return True
        return False

    def verify_recovery(self) -> bool:
        status, _ = self._request("/items")
        if status == 200:
            self.recovered_at = datetime.now(timezone.utc)
            return True
        return False

    def cleanup(self) -> None:
        self._request(
            "/test/faults/reset",
            method="POST",
            headers={"X-Titan-Fault-Auth": self.auth_token}
        )
        self.completed_at = datetime.now(timezone.utc)
