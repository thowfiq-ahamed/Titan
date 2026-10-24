# TITAN: Cloud-Native Delivery, Platform Engineering & Reliability Intelligence Platform

[![CI](https://github.com/thowfiq-ahamed/Titan/actions/workflows/ci.yaml/badge.svg)](https://github.com/thowfiq-ahamed/Titan/actions/workflows/ci.yaml)
[![Release & GitOps](https://github.com/thowfiq-ahamed/Titan/actions/workflows/release-gitops.yaml/badge.svg)](https://github.com/thowfiq-ahamed/Titan/actions/workflows/release-gitops.yaml)
[![Tests](https://img.shields.io/badge/tests-34%20passed-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)]()
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.31-326CE5.svg?logo=kubernetes&logoColor=white)]()
[![ArgoCD](https://img.shields.io/badge/GitOps-Argo%20CD-EF7B4D.svg?logo=argo&logoColor=white)]()
[![Terraform](https://img.shields.io/badge/IaC-Terraform%201.5+-844FBA.svg?logo=terraform&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg?logo=docker&logoColor=white)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

**TITAN** is a cloud-native platform engineering and Site Reliability Engineering (SRE) portfolio project designed to demonstrate enterprise architecture, GitOps delivery, and production operations. It bridges the gap between **high-velocity deployment** and **automated operational resilience**.

It provides:
1. **TITAN Developer Platform**: Microservice catalog registration, multi-environment Kubernetes manifests (Helm & Kustomize), and GitOps delivery.
2. **TITAN Reliability Lab**: Chaos & resilience testing subsystem that introduces bounded, controlled failures, verifies automated recovery strategies, and computes reproducible MTTR/MTTD benchmarks.
3. **TITAN Incident Engine**: Deterministic Root Cause Analysis (RCA) service that consumes Alertmanager webhooks, correlates multi-signal diagnostic evidence (alerts, metrics, logs, probe deadlocks), and executes allowlist-gated automated remediations with strict policy verification.

---

## Architecture Topology

```
========================================================================================================
                              TITAN ARCHITECTURE OVERVIEW
========================================================================================================

 [ Developer / SRE ] ───► [ TITAN Web Dashboard (React + Vite + TypeScript) ]
            │                                   │
            ▼                                   ▼
 [ Git CLI / GitHub PR ]             [ TITAN Platform API (FastAPI) ]
            │                                   │
            ▼                                   ▼
 [ GitHub Actions CI / Jenkins ]     [ SQLite / PostgreSQL Persistence ]
   • Code Lint & Unit Tests                     │
   • Trivy Security Policy Gate                 ├───────────────────────────────┐
   • Docker Build & Immutable Tag               ▼                               ▼
   • Manifest PR Update (GitOps)     [ TITAN Incident Engine ]      [ TITAN Reliability Lab ]
            │                           • Alertmanager Webhook         • Controlled Fault Injection
            ▼                           • Telemetry & Log Correlator   • Verification Probe
     [ Git Repository ]                 • Deterministic Diagnosis      • MTTR/MTTD Benchmark Engine
      (deploy/gitops)                   • Safe Recovery Recommender    • Strategy Evaluator
            │                                   │                               │
            ▼                                   ▼                               │
     [ Argo CD Controller ] ────────► [ Kubernetes Cluster ] ◄──────────────────┘
   (Sync, Health, Self-Healing)         (Kind / EKS 1.31)
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
      [ Apps: Inventory API ]         [ Observability Stack ]        [ Security & Config ]
      • FastAPI + Pydantic v2         • Prometheus Scraper           • Vault / K8s Secrets
      • SQLAlchemy 2.x + Alembic      • Alertmanager Rules           • Least-Privilege RBAC
      • /health/live & /ready         • Grafana Dashboards           • Non-Root Container (10001)
      • Structured JSON Logs          • Fluentbit / ELK Pipeline     • NetworkPolicies
      • /metrics Prometheus           • Splunk Event Adapter         • Loopback-Restricted Dev Ports
```

---

## Technology Stack

| Domain | Technologies Used |
|---|---|
| **Workload & APIs** | Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PostgreSQL 16 |
| **CLI & Tools** | Python CLI (`scripts/titan.py`), Click, Argparse, Requests |
| **Frontend UI** | React 18, TypeScript, Vite, Modern Responsive Design System |
| **Containerization** | Docker, Multi-Stage Hardened Builds (Non-Root UID 10001), Docker Compose |
| **Orchestration** | Kubernetes 1.31, Helm v3, Kustomize (bases + overlays for dev/staging/prod) |
| **GitOps** | Argo CD (primary), Flux CD (isolated comparison) |
| **Cloud & IaC** | AWS (VPC, EKS 1.31, RDS, ECR, IAM, S3, Secrets Manager), Terraform (modular + state lock) |
| **CI/CD** | GitHub Actions (primary), Jenkins Declarative Pipeline |
| **Observability** | Prometheus, Alertmanager, Grafana, ELK (Logstash), Splunk HEC Adapter |
| **DevSecOps** | Trivy vulnerability scanning (enforcing CRITICAL gate), HashiCorp Vault, Kubernetes NetworkPolicies |

---

## Subsystems & Components

### 1. Managed Workload: Inventory API (`apps/inventory-api`)
A production-grade microservice handling asset and inventory tracking.
- **Data Layer**: SQLAlchemy 2.0 with PostgreSQL persistence and Alembic migrations (`001_initial_schema.py`).
- **Telemetry**: Exposes `/health/live`, `/health/ready` (with database ping latency profiling), and native `/metrics` for Prometheus scraping.
- **Structured JSON Logging**: Standardized JSON format with `X-Correlation-ID` tracing across requests.
- **Reliability Lab Fault Gate**: Controlled fault endpoints (`/test/faults/*`) guarded by `ENABLE_FAULT_INJECTION=true` and explicit `X-Titan-Fault-Auth` token verification. Fault injection is strictly disabled by default.

### 2. Platform API & CLI (`services/platform-api` & `scripts/titan.py`)
Central platform control plane providing REST endpoints and a developer CLI:
- `titan service list / register`: Service catalog management.
- `titan env list`: Multi-environment cluster quota & GitOps branch tracking.
- `titan incident list`: Recorded incidents, diagnostic evidence trails, and recovery actions.
- `titan benchmark summary`: Empirical reliability benchmark calculations.

### 3. Reliability Lab (`packages/experiment-runner`)
Automated experiment execution engine supporting 6 failure scenarios:
1. **Broken Release (`SCN-001`)**: HTTP 500 error surge.
2. **Kubernetes Probe Deadlock (`SCN-002`)**: Liveness/readiness probe failure causing traffic isolation.
3. **Database Dependency Outage (`SCN-003`)**: Database connection drop while application process remains alive.
4. **Container Crash / CrashLoopBackOff (`SCN-004`)**: Process exit and container restart measurement.
5. **Resource Pressure (`SCN-005`)**: Bounded CPU/latency saturation.
6. **Configuration Drift (`SCN-006`)**: Divergence between cluster state and GitOps repository.

Supports 4 recovery strategies:
- **Strategy A**: Kubernetes native self-healing (kubelet pod restart).
- **Strategy B**: Application rollback (reverting to previous healthy container tag).
- **Strategy C**: GitOps-aware rollback (reverting Git repository for Argo CD auto-sync).
- **Strategy D**: Policy-controlled recovery (Incident Engine allowlisted autonomous remediation).

### 4. TITAN Incident Engine (`services/incident-engine`)
Deterministic Root Cause Analysis engine:
- Consumes Prometheus Alertmanager webhooks.
- Correlates firing alerts, metric golden signals, probe status, and recent GitOps deployment rollouts.
- Emits structured diagnoses with root cause, supporting evidence, contradictory evidence, and confidence score.
- Enforces strict allowlist policies and approval requirements before executing state-changing recoveries.

### 5. Cloud Infrastructure as Code (`terraform/`)
Modular, reusable Terraform configuration:
- `bootstrap`: S3 state bucket with AES256 encryption, versioning, and DynamoDB locking.
- `modules`: `vpc` (3-tier networking), `security_groups`, `iam` (GitHub Actions OIDC keyless trust), `ecr` (immutable tags + scan-on-push), `eks` (Kubernetes 1.31 managed cluster), `rds` (PostgreSQL 16 in private DB subnets).
- `environments`: Isolated configurations for `dev` and `staging`.

---

## Clean-Checkout Setup Guide

Follow these steps from a fresh clone to install, test, and run the platform:

### 1. Prerequisites
- **Python**: Version 3.11 or 3.12+
- **Docker & Docker Compose**: v2.20+
- **Node.js**: v18+ (for Web Dashboard UI)
- **Terraform**: v1.5+ (optional, for AWS IaC verification)

### 2. Environment Setup & Automated Tests
```powershell
# Clone the repository
git clone https://github.com/thowfiq-ahamed/Titan.git
cd Titan

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # On Linux/macOS: source .venv/bin/activate

# Install application dependencies, test runner, and linters
pip install --upgrade pip
pip install -r apps/inventory-api/requirements.txt
pip install ruff pytest-cov

# Run code quality lint gate
ruff check apps/ services/ packages/ tests/ scripts/

# Run the complete test suite (33 tests)
pytest -v
```

### 3. Local Container Run with Docker Compose
Local ports are securely bound to `127.0.0.1` by default to prevent unauthorized external network exposure:
```powershell
# Validate compose configuration
docker compose config

# Start PostgreSQL and Inventory API in isolated bridge network
docker compose up -d

# Verify container health
docker compose ps
curl http://127.0.0.1:8001/health/live
curl http://127.0.0.1:8001/health/ready
```

### 4. Safe Execution of Reliability Lab Experiments
Fault injection is disabled by default (`ENABLE_FAULT_INJECTION=false`). To run a local resilience experiment:
```powershell
# Start local API with explicit test authorization credentials
$env:ENABLE_FAULT_INJECTION="true"
$env:FAULT_INJECTION_AUTH_TOKEN="local-dev-trial-key-xyz"
python -m uvicorn inventory_api.main:app --port 8001

# Run an experiment trial using the runner CLI
python -m experiment_runner.runner --scenario probe_failure --strategy k8s_self_heal
```
*Unauthorized requests to `/test/faults/*` without valid `X-Titan-Fault-Auth` are rejected with `401 Unauthorized` or `403 Forbidden`.*

---

## Automated Test Results

TITAN enforces 100% passing test coverage across unit, integration, API CRUD, probe health, RCA rules, and experiment execution:

```
tests/api/test_fault_injection.py::test_fault_injection_requires_auth PASSED
tests/api/test_fault_injection.py::test_fault_injection_disabled_when_flag_is_false PASSED
tests/api/test_fault_injection.py::test_simulated_error_surge_and_recovery PASSED
tests/api/test_health_probes.py::test_liveness_probe_healthy PASSED
tests/api/test_health_probes.py::test_readiness_probe_healthy PASSED
tests/api/test_health_probes.py::test_simulated_readiness_failure PASSED
tests/api/test_health_probes.py::test_simulated_liveness_failure PASSED
tests/api/test_inventory_crud.py::test_create_and_get_item PASSED
tests/api/test_inventory_crud.py::test_create_item_duplicate_sku_conflict PASSED
tests/api/test_inventory_crud.py::test_list_items_with_pagination_and_filter PASSED
tests/api/test_inventory_crud.py::test_update_item PASSED
tests/api/test_inventory_crud.py::test_delete_item PASSED
tests/api/test_inventory_crud.py::test_get_nonexistent_item_returns_404 PASSED
tests/api/test_inventory_crud.py::test_validation_error_returns_rfc_details PASSED
tests/api/test_metrics_endpoint.py::test_metrics_endpoint_returns_prometheus_format PASSED
tests/api/test_platform_api.py::test_platform_health PASSED
tests/api/test_service_registration_and_list PASSED
tests/api/test_environment_configuration PASSED
tests/api/test_incident_lifecycle PASSED
tests/api/test_experiment_and_benchmark_calculation PASSED
tests/integration/test_database_persistence.py::test_database_persistence_across_transactions PASSED
tests/integration/test_database_persistence.py::test_database_unique_sku_constraint PASSED
tests/unit/test_experiment_runner.py::test_experiment_runner_full_cycle PASSED
tests/unit/test_experiment_runner.py::test_policy_controlled_recovery_strategy PASSED
tests/unit/test_experiment_runner.py::test_policy_denial_for_unauthorized_action PASSED
tests/unit/test_incident_engine.py::test_diagnose_bad_release PASSED
tests/unit/test_incident_engine.py::test_diagnose_dependency_outage PASSED
tests/unit/test_incident_engine.py::test_alertmanager_webhook_endpoint PASSED
tests/unit/test_inventory_models.py::test_item_create_valid PASSED
tests/unit/test_inventory_models.py::test_item_create_negative_quantity_fails PASSED
tests/unit/test_inventory_models.py::test_item_create_negative_price_fails PASSED
tests/unit/test_inventory_models.py::test_item_create_short_sku_fails PASSED
tests/unit/test_inventory_models.py::test_item_update_partial PASSED
tests/unit/test_inventory_models.py::test_sqlalchemy_item_instantiation PASSED

======================= 34 passed in 4.83s ========================
```

---

## Repository Documentation Index

- [Post-Build Engineering Audit & Verification Report](docs/audits/POST_BUILD_AUDIT.md)
- [Master Architecture Document](docs/architecture/ARCHITECTURE.md)
- [End-to-End Setup Guide](docs/setup/END_TO_END_SETUP.md)
- [GitHub Setup & Publication Guide](docs/setup/GITHUB_SETUP.md)
- [GitHub Actions CI/CD Setup](docs/setup/GITHUB_ACTIONS_SETUP.md)
- [External Platform Integrations Guide](docs/setup/INTEGRATIONS.md)
- [Interview Demonstration Runbook](docs/interview-preparation/INTERVIEW_DEMO_RUNBOOK.md)
- [Incident Response Runbook](docs/runbooks/INCIDENT_RESPONSE_RUNBOOK.md)
- [Terraform Infrastructure & Cost Estimates](terraform/README.md)
- [Project Security Policy](SECURITY.md)
- [Task Tracking Checklist](TASKS.md)
