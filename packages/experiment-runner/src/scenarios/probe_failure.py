"""
Scenario SCN-002: Probe Failure (Readiness & Liveness Deadlock)
Simulates probe failure leading to service isolation or pod restart.
"""

from typing import Dict, Any
from datetime import datetime, timezone
import urllib.request
import urllib.error
import json
from .base import BaseScenario


class ProbeFailureScenario(BaseScenario):
    def __init__(self, probe_type: str = "readiness", target_url: str = "http://localhost:8001", auth_token: str = "dev-reliability-test-key-32ch"):
        super().__init__(
            scenario_id="SCN-002",
            name=f"Kubernetes {probe_type.title()} Probe Failure",
            description=f"Simulates {probe_type} probe failure causing service removal from endpoint slice",
            target_service="inventory-api",
            target_environment="dev"
        )
        self.probe_type = probe_type
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
        path = f"/health/{self.probe_type if self.probe_type == 'live' else 'ready'}"
        status, body = self._request(path)
        return status == 200

    def inject_fault(self) -> Dict[str, Any]:
        self.fault_injected_at = datetime.now(timezone.utc)
        status, body = self._request(
            "/test/faults/probe",
            method="POST",
            payload={"probe_type": self.probe_type, "fail": True},
            headers={"Content-Type": "application/json", "X-Titan-Fault-Auth": self.auth_token}
        )
        return {"status_code": status, "payload": body}

    def check_detection_signal(self) -> bool:
        path = f"/health/{'live' if self.probe_type == 'liveness' else 'ready'}"
        status, _ = self._request(path)
        expected_status = 500 if self.probe_type == "liveness" else 503
        if status == expected_status:
            self.detected_at = datetime.now(timezone.utc)
            return True
        return False

    def verify_recovery(self) -> bool:
        path = f"/health/{'live' if self.probe_type == 'liveness' else 'ready'}"
        status, _ = self._request(path)
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
