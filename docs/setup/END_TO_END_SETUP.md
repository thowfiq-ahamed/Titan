# TITAN Platform: End-to-End Setup & Demonstration Guide

This step-by-step runbook takes you from a clean repository checkout to a fully verified reliability engineering demonstration.

---

## Stage A: Local Development & Verification

### 1. Prerequisites Check
Ensure the following tools are installed on your workstation:
- Python 3.11+
- Git 2.40+
- Docker & Docker Compose (optional for local SQLite execution)
- kubectl 1.28+ and Terraform 1.5+

### 2. Environment Setup
```powershell
# 1. Activate Python virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Run all automated tests (33 tests covering CRUD, health, metrics, RCA, and runner)
pytest -v

# 3. Start Inventory API locally
$env:PYTHONPATH="apps/inventory-api"
$env:DATABASE_URL="sqlite:///./inventory.db"
$env:ENABLE_FAULT_INJECTION="true"
python -m uvicorn inventory_api.main:app --host 0.0.0.0 --port 8001
```

### 3. Verify Health & Telemetry
In a separate terminal:
```powershell
# Verify liveness
Invoke-RestMethod http://localhost:8001/health/live

# Verify readiness & database ping latency
Invoke-RestMethod http://localhost:8001/health/ready

# Inspect Prometheus metrics
(Invoke-WebRequest http://localhost:8001/metrics).Content
```

---

## Stage B: GitHub Repository & CI Setup

1. Follow [`GITHUB_SETUP.md`](GITHUB_SETUP.md) to audit git hygiene and link to your GitHub account.
2. Push branch `main`. GitHub Actions will automatically execute `.github/workflows/ci.yaml`:
   - Linting check
   - 33 automated tests with coverage
   - Kustomize overlay manifest validation
   - Trivy container security vulnerability scan

---

## Stage C: Container Registry Publication

1. Publish the container image with an immutable tag:
   ```bash
   docker build -t ghcr.io/<ORG>/titan-inventory-api:v1.0.0 -f apps/inventory-api/Dockerfile apps/inventory-api
   docker push ghcr.io/<ORG>/titan-inventory-api:v1.0.0
   ```
2. Verify image scanning on GHCR or Amazon ECR.

---

## Stage D: Local Kubernetes & GitOps Reconciliation

1. Create a local cluster:
   ```bash
   kind create cluster --name titan-local
   ```
2. Deploy the workload using Kustomize:
   ```bash
   kubectl apply -k deploy/kustomize/overlays/dev
   ```
3. Check pod status:
   ```bash
   kubectl get pods -n titan-dev
   kubectl get services -n titan-dev
   ```
4. (Optional) Deploy Argo CD via `gitops/argocd/application-dev.yaml` to observe automated self-healing.

---

## Stage E: AWS Cloud Infrastructure Verification

1. Review the Terraform configuration:
   ```bash
   cd terraform/environments/dev
   terraform fmt -check
   terraform validate
   ```
2. Note the cost estimate in `terraform/README.md` (~$182/mo).
3. Obtain explicit authorization before running `terraform apply`.

---

## Stage F: Controlled Failure & Reliability Intelligence Demonstration

This is the central portfolio demonstration showing automated failure detection, diagnosis, recovery, and benchmarking:

1. **Start the Platform API & Incident Engine**:
   ```powershell
   $env:PYTHONPATH="services/platform-api:services/incident-engine:packages/common-models:."
   python -m uvicorn platform_api.main:app --host 0.0.0.0 --port 8000
   ```
2. **Trigger Controlled Fault via Reliability Lab**:
   ```powershell
   # Inject broken release (HTTP 500 error surge)
   $headers = @{"X-Titan-Fault-Auth"="dev-reliability-test-key-32ch"}
   Invoke-RestMethod -Method Post -Uri http://localhost:8001/test/faults/error-surge -Headers $headers -Body '{"enabled":true,"percentage":100}' -ContentType "application/json"
   ```
3. **Observe Automated Incident Engine Diagnosis**:
   - Prometheus Alertmanager catches elevated 5xx rate.
   - Webhook triggers `incident_engine.rules.diagnose_incident`.
   - Incident is diagnosed as `bad_release` with confidence `0.98`.
   - Supporting evidence logged: high error rate, recent deployment correlation.
4. **Execute Policy-Controlled Recovery**:
   - Authorized recovery strategy `app_rollback` is approved and executed.
   - Fault is cleared; workload restored to baseline.
5. **Verify Service Recovery & Generate Benchmark Report**:
   ```powershell
   python scripts/titan.py benchmark summary
   ```
   Inspect recorded MTTD, MTTR, diagnosis accuracy, and strategy breakdown!
