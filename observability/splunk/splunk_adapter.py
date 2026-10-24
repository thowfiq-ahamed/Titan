"""
TITAN Splunk Integration Adapter
Formats and ships security and reliability audit events to Splunk HTTP Event Collector (HEC).
Runs safely in simulation mode when credentials are not configured (Rule 9).
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any

SPLUNK_HEC_URL = os.environ.get("SPLUNK_HEC_URL", "")
SPLUNK_HEC_TOKEN = os.environ.get("SPLUNK_HEC_TOKEN", "")
ENABLE_SPLUNK = os.environ.get("ENABLE_SPLUNK_ADAPTER", "false").lower() == "true"


def ship_event_to_splunk(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ships a structured operational/security event to Splunk HEC.
    Returns: {"status": "shipped" | "simulated" | "failed", "detail": str}
    """
    event_packet = {
        "time": int(time.time()),
        "host": "titan-platform",
        "source": "titan:audit",
        "sourcetype": "_json",
        "event": {
            "event_type": event_type,
            "platform_version": "1.0.0",
            "data": payload
        }
    }

    if not ENABLE_SPLUNK or not SPLUNK_HEC_URL or not SPLUNK_HEC_TOKEN:
        return {
            "status": "simulated",
            "detail": "Splunk adapter running in safe local simulation mode (no external token provided).",
            "event_preview": event_packet
        }

    try:
        headers = {
            "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
            "Content-Type": "application/json"
        }
        data = json.dumps(event_packet).encode("utf-8")
        req = urllib.request.Request(SPLUNK_HEC_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as res:
            return {"status": "shipped", "code": res.status}
    except Exception as exc:
        return {"status": "failed", "error": str(exc)}
