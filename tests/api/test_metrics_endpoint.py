"""
API tests for Prometheus Metrics endpoint.
"""

from fastapi.testclient import TestClient


def test_metrics_endpoint_returns_prometheus_format(client: TestClient):
    # Make a few API calls to trigger metric increment
    client.get("/health/live")
    client.get("/health/ready")

    res = client.get("/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    body = res.text

    assert "titan_http_requests_total" in body
    assert "titan_http_request_duration_seconds" in body
    assert "titan_inventory_items_total" in body
