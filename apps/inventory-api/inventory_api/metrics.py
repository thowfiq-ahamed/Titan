"""
TITAN Inventory API - Prometheus Metrics Instrumentation
Exposes standard golden signals: rate, errors, duration, and domain gauges.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# 1. Traffic & Golden Signals
HTTP_REQUESTS_TOTAL = Counter(
    "titan_http_requests_total",
    "Total count of HTTP requests processed by Inventory API",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "titan_http_request_duration_seconds",
    "HTTP request latency histogram in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# 2. Domain & Application State
INVENTORY_ITEMS_TOTAL = Gauge(
    "titan_inventory_items_total",
    "Current number of inventory items registered in persistence store"
)

DATABASE_ERRORS_TOTAL = Counter(
    "titan_database_errors_total",
    "Count of database connection or query failures encountered",
    ["operation"]
)

# 3. Reliability Lab Metrics
SIMULATED_FAULTS_TOTAL = Counter(
    "titan_simulated_faults_total",
    "Count of controlled faults injected during reliability testing",
    ["fault_type"]
)


def get_metrics_response() -> Response:
    """Returns the Prometheus metrics scrape payload."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
