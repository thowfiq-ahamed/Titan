# TITAN Platform: Interview-Ready Live Technical Demonstration Runbook

This runbook provides a scripted, repeatable 10-minute live demonstration of the **TITAN** platform for technical interviews (DevOps / SRE / Platform Engineering).

---

## 1. Architectural Narrative (2 Minutes)

**Speaking Track:**
> *"TITAN is a cloud-native platform engineering and Site Reliability Engineering system designed to solve the critical gap between deployment velocity and operational resilience.*
> *It features two core subsystems:*
> 1. *A standardized Developer Platform that abstracts Kubernetes packaging, least-privilege security controls, and GitOps delivery via Argo CD.*
> 2. *A Reliability Lab and Deterministic Incident Engine that introduces controlled failures, extracts multi-signal diagnostic evidence (alerts, metrics, logs, probe deadlocks), verifies recovery outcomes, and calculates empirical MTTR and MTTD benchmarks."*

---

## 2. Live Technical Walkthrough (8 Minutes)

### Step 1: Quality, Test Suite & Health Probes (1 Min)
Show that the system is real, working software with 33 passing automated tests:
```powershell
.\.venv\Scripts\pytest.exe -v
```
Point out:
- Unit, API CRUD, probe health, and fault injection tests passing in ~1 second.
- Liveness and readiness endpoints with database query latency profiling (`/health/live`, `/health/ready`).

### Step 2: The Service Catalog & Developer Experience (1 Min)
Open the TITAN Dashboard at `http://localhost:3000` or show the `titan` CLI:
```powershell
python scripts/titan.py service list
python scripts/titan.py env list
```
Show:
- Central service registry with tiers (`tier-0` mission-critical down to `tier-2`).
- Environment quotas (CPU/Memory limits, replica policies, GitOps branch targeting).

### Step 3: GitOps Delivery Chain (1 Min)
Show the Kustomize overlays and Argo CD application manifests:
- `deploy/kustomize/overlays/dev/kustomization.yaml`
- Explain the promotion workflow: PR merge -> GitHub Actions CI tests & Trivy scan -> immutable container digest -> GitOps commit -> Argo CD automated reconciliation without manual kubectl mutations.

### Step 4: The Controlled Failure (Reliability Lab) (2 Mins)
Navigate to **Reliability Lab** in the dashboard, or trigger via PowerShell:
```powershell
# Inject Scenario SCN-001: Broken Release HTTP 500 error surge
$headers = @{"X-Titan-Fault-Auth"="dev-reliability-test-key-32ch"}
Invoke-RestMethod -Method Post -Uri http://localhost:8001/test/faults/error-surge -Headers $headers -Body '{"enabled":true,"percentage":100}' -ContentType "application/json"
```
Verify the error surge:
```powershell
Invoke-RestMethod http://localhost:8001/items
# Returns HTTP 500 SimulatedInternalError with correlation ID
```

### Step 5: Incident Engine Telemetry & Deterministic RCA (2 Mins)
Demonstrate automated detection and diagnosis:
1. Prometheus fires `TitanHighErrorRate`.
2. Alertmanager forwards alert to `http://localhost:8002/api/v1/alerts`.
3. The Incident Engine diagnoses root cause with 98% confidence:
   - **Suspected Cause**: *Defective release code throwing internal server errors (HTTP 500 surge)*
   - **Supporting Evidence**: Alert firing + recent deployment rollout detected within window.
   - **Recommended Strategy**: `app_rollback` (Security allowlist policy verified).

Inspect in CLI:
```powershell
python scripts/titan.py incident list
```

### Step 6: Verified Recovery & Empirical Benchmarking (1 Min)
Execute approved rollback / reset:
```powershell
$headers = @{"X-Titan-Fault-Auth"="dev-reliability-test-key-32ch"}
Invoke-RestMethod -Method Post -Uri http://localhost:8001/test/faults/reset -Headers $headers
```
Verify health recovery:
```powershell
Invoke-RestMethod http://localhost:8001/items
# Returns HTTP 200 with normal catalog data
```
Display the final quantitative benchmark report:
```powershell
python scripts/titan.py benchmark summary
```
Show:
- **Mean Time To Detect (MTTD)**: Real recorded seconds.
- **Mean Time To Recover (MTTR)**: Real recovery timeline.
- **Strategy Comparison**: Empirical effectiveness of Kubernetes self-healing vs Automated Rollback vs Policy-Controlled Remediation.
