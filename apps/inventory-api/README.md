# TITAN Inventory API (`apps/inventory-api`)

The **TITAN Inventory API** is the managed production workload used to demonstrate TITAN's deployment, GitOps reconciliation, observability, and controlled reliability experiments.

---

## 1. Features

- **FastAPI Framework**: High performance async/sync routing with automatic OpenAPI docs (`/docs`).
- **Database Persistence**: SQLAlchemy 2.0 ORM with PostgreSQL persistence and Alembic schema migrations. (Zero-dependency SQLite compatibility for local testing).
- **Golden Signals Observability**:
  - `/health/live`: Process liveness probe.
  - `/health/ready`: Database dependency readiness probe with query latency profiling.
  - `/metrics`: Native Prometheus scrape endpoint with request counts, duration histograms, item gauges, and error metrics.
  - Structured JSON logging with `X-Correlation-ID` context propagation across all requests.
- **Reliability Lab Fault Injection Engine**:
  - Gated by `ENABLE_FAULT_INJECTION=true` and authenticated via `X-Titan-Fault-Auth`.
  - Simulates Kubernetes probe failures, artificial latency, and HTTP 500 error surges (bad release simulation).
- **Security & Container Hardening**:
  - Multi-stage `Dockerfile` running as unprivileged user (`appuser` UID 10001).
  - RFC 7807 compliant error envelopes.

---

## 2. API Endpoints

| Method | Path | Description | Auth Required |
|---|---|---|---|
| `GET` | `/health/live` | Kubernetes Liveness Probe | No |
| `GET` | `/health/ready` | Kubernetes Readiness Probe | No |
| `GET` | `/metrics` | Prometheus Metrics Scrape Endpoint | No |
| `GET` | `/items` | List inventory items (supports pagination & filtering) | No |
| `POST` | `/items` | Create new inventory item (validates unique SKU) | No |
| `GET` | `/items/{id}` | Retrieve item by UUID | No |
| `PUT` | `/items/{id}` | Update existing inventory item | No |
| `DELETE` | `/items/{id}` | Delete item from catalog | No |
| `GET` | `/test/faults/status` | Inspect active simulated faults | Yes (`X-Titan-Fault-Auth`) |
| `POST` | `/test/faults/probe` | Inject simulated probe failure (`liveness`/`readiness`) | Yes (`X-Titan-Fault-Auth`) |
| `POST` | `/test/faults/latency`| Inject artificial service delay | Yes (`X-Titan-Fault-Auth`) |
| `POST` | `/test/faults/error-surge` | Inject simulated bad release HTTP 500 surge | Yes (`X-Titan-Fault-Auth`) |
| `POST` | `/test/faults/reset` | Restore normal healthy baseline | Yes (`X-Titan-Fault-Auth`) |

---

## 3. Local Development & Testing

### Running Tests
```powershell
# From repository root
.\.venv\Scripts\pytest.exe -v
```

### Running Locally with Python
```powershell
$env:PYTHONPATH="apps/inventory-api"
$env:DATABASE_URL="sqlite:///./inventory.db"
$env:ENABLE_FAULT_INJECTION="true"
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Running with Docker Compose
```bash
docker compose up -d --build
```
Verify endpoints:
- Swagger Docs: [http://localhost:8001/docs](http://localhost:8001/docs)
- Readiness Probe: [http://localhost:8001/health/ready](http://localhost:8001/health/ready)
- Metrics: [http://localhost:8001/metrics](http://localhost:8001/metrics)
