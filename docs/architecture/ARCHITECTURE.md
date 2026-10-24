# TITAN: Architecture Specification & System Design
**Cloud-Native Delivery, Platform Engineering & Reliability Intelligence Platform**

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
   • Trivy / Snyk Security Scan                 ├───────────────────────────────┐
   • Docker Build & Immutable Tag               ▼                               ▼
   • Manifest Update (GitOps)        [ TITAN Incident Engine ]      [ TITAN Reliability Lab ]
            │                           • Alertmanager Webhook         • Controlled Fault Injection
            ▼                           • Telemetry & Log Correlator   • Verification Probe
     [ Git Repository ]                 • Deterministic Diagnosis      • MTTR/MTTD Benchmark Engine
      (deploy/gitops)                   • Safe Recovery Recommender    • Strategy Evaluator
            │                                   │                               │
            ▼                                   ▼                               │
     [ Argo CD Controller ] ────────► [ Kubernetes Cluster ] ◄──────────────────┘
   (Sync, Health, Self-Healing)         (Kind / EKS)
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
      [ Apps: Inventory API ]         [ Observability Stack ]        [ Security & Config ]
      • FastAPI + Pydantic v2         • Prometheus Scraper           • Vault / K8s Secrets
      • SQLAlchemy 2.x + Alembic      • Alertmanager Rules           • Least-Privilege RBAC
      • /health/live & /ready         • Grafana Dashboards           • Non-Root Container
      • Structured JSON Logs          • Fluentbit / ELK Pipeline     • NetworkPolicies
      • /metrics Prometheus           • Splunk Event Adapter
```

---

## 1. System Vision & Problem Statement

Modern cloud-native engineering faces a critical gap between **deployment velocity** and **operational resilience**:
- Applications are pushed rapidly via CI/CD, but configuration drift, broken dependencies, probe misconfigurations, and resource exhaustion cause production incidents.
- SRE teams often rely on ad-hoc triage, slow manual root-cause analysis (RCA), and unverified recovery steps.

**TITAN** solves this by unifying:
1. **Standardized Developer Platform**: Centralized application registration, environment-specific manifest generation, and deployment health tracking.
2. **Deterministic Incident Engine**: Real-time correlation of alerts, metrics, pod events, container logs, and deployment revisions into explainable root causes.
3. **Reliability Lab**: Controlled failure injection engine measuring the empirical effectiveness of automated recovery strategies (Kubernetes self-healing, GitOps rollbacks, policy-controlled remediations).

---

## 2. Subsystems & Component Boundaries

### Subsystem 1: Managed Workload — Inventory API (`apps/inventory-api`)
- **Framework**: Python FastAPI, SQLAlchemy 2.0, Pydantic v2 schemas.
- **Database**: PostgreSQL (with SQLite compatibility for fast local tests) + Alembic migrations.
- **Standard Observability**: Structured JSON logging with `X-Correlation-ID` propagation, Prometheus `/metrics` endpoint.
- **Health Verification**: `/health/live` (process alive) and `/health/ready` (database ping & dependency checks).
- **Controlled Fault Injection**: Protected test endpoints `/test/faults/{type}` active **only** when `ENABLE_FAULT_INJECTION=true` (simulating latency, DB connection drops, probe failures, and memory/CPU pressure).

### Subsystem 2: TITAN Platform API (`services/platform-api`)
- **Framework**: FastAPI REST API + CLI (`titan`).
- **Core Entities**:
  - `Service`: Registered workloads, git repositories, image repos, environment configurations.
  - `Environment`: Dev, Staging, Prod with resource limits and security policies.
  - `Incident`: Recorded alerts, evidence trails, diagnostic hypotheses, and recovery status.
  - `Experiment`: Controlled reliability test configurations, schedules, and run records.
  - `Benchmark`: Quantitative MTTR, MTTD, accuracy, and blast-radius scores.

### Subsystem 3: TITAN Incident Engine (`services/incident-engine`)
- **Ingestion**: Prometheus Alertmanager webhooks, Kubernetes watch events, log aggregators.
- **Rule Engine**: Deterministic diagnosis rules classifying failure types:
  - `BAD_RELEASE`: CrashLoopBackOff or HTTP 5xx surge immediately following image tag change.
  - `DEPENDENCY_OUTAGE`: Database connection timeouts while app process is running.
  - `RESOURCE_EXHAUSTION`: OOMKilled containers or CPU throttling.
  - `PROBE_FAILURE`: Unhealthy readiness probes causing pod isolation.
  - `CONFIG_DRIFT`: Cluster state deviating from GitOps desired state.
- **Safety Gate**: Strict allowlist of remediation actions; requires explicit confirmation in protected environments; zero shell execution from alert payloads.

### Subsystem 4: TITAN Reliability Lab (`packages/experiment-runner`)
- **Scenarios**:
  1. Broken Release (HTTP 500 error injection)
  2. Repeated Container Crash (CrashLoopBackOff simulation)
  3. Database Dependency Outage (DB connection block)
  4. CPU / Memory Pressure (Bounded resource saturation)
  5. Readiness / Liveness Probe Failure
  6. GitOps Configuration Drift
- **Evaluation Engine**: Automated measurement of MTTD (Detection), Time to Diagnosis, MTTR (Recovery), Recovery Success Rate, and GitOps Desired-State Consistency.

### Subsystem 5: User Interface (`frontend`)
- **Stack**: React 18, TypeScript, Vite, Tailwind CSS / Modern CSS design system.
- **Views**:
  1. Overview & Health Dashboard
  2. Service Catalog & Registration
  3. Service Details & Telemetry
  4. Incident Center & Root Cause Visualizer
  5. Reliability Lab & Experiment Launcher
  6. Benchmark Reports & Strategy Comparison
  7. Deployment History & GitOps Status
  8. Settings & Integration Status

---

## 3. Technology & Architecture Decision Records (ADRs)

| ADR ID | Decision | Chosen Option | Rationale |
|---|---|---|---|
| **ADR-001** | Workload & API Framework | FastAPI + Pydantic v2 | High-performance, automatic OpenAPI documentation, strict type validation, native async support. |
| **ADR-002** | Database & Migration Tool | PostgreSQL + SQLAlchemy 2.0 + Alembic | Industry standard relational persistence with robust migration management. SQLite fallback for zero-dependency unit tests. |
| **ADR-003** | GitOps Tooling | Argo CD (primary) & Flux CD (isolated comparison) | Declarative K8s deployment with Git as the single source of truth; clear self-healing mechanics. |
| **ADR-004** | Incident Engine Architecture | Deterministic Rules Engine with Structured Evidence | Transparent, auditable, explainable root-cause diagnosis without hallucination risks. |
| **ADR-005** | Cloud Infrastructure | Terraform with Modular AWS Architecture (EKS, RDS, VPC) | Reusable, reproducible infrastructure-as-code with remote state locking and least-privilege IAM. |
| **ADR-006** | Observability Foundation | Prometheus + Alertmanager + Grafana | Standard CNCF telemetry stack with native Kubernetes integration and webhook capabilities. |

---

## 4. Phase-by-Phase Roadmap

- **Phase 0**: Architecture, Workspace Isolation, and Task Checklist (Completed)
- **Phase 1**: Working Local Application (Inventory API, PostgreSQL persistence, Alembic, tests, Docker, Compose)
- **Phase 2**: Platform API & Data Models (Service registration, environment configs, health tracking)
- **Phase 3**: Reliability Lab & Experiment Runner (Scenarios, failure injection, benchmark calculations)
- **Phase 4**: Kubernetes & GitOps (Helm charts, Kustomize, Argo CD manifests, rollback verification)
- **Phase 5**: CI/CD & DevSecOps (GitHub Actions workflows, Trivy scanning, Jenkins pipeline)
- **Phase 6**: Observability & Incident Engine (Prometheus metrics, Alertmanager webhook, RCA engine)
- **Phase 7**: Terraform & Cloud Infrastructure (VPC, EKS, RDS, IAM modules, cost estimation)
- **Phase 8**: External Integrations & Setup Guides (GHCR, ECR, Vault, ELK, Splunk, Snyk)
- **Phase 9**: Repository Review & Safe GitHub Handover (Hygiene audit, security checks)
- **Phase 10**: Portfolio Demonstration & Interview Runbooks (End-to-end repeatable script)
