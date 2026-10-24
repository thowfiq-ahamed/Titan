# TITAN Incident Response Runbook

## On-Call SRE Operational Guide

This runbook defines operational procedures for triaging, diagnosing, remediating, and reviewing production and staging incidents across the TITAN platform.

---

## 1. Incident Severity Definitions

- **P1 (Critical)**: Customer-facing service down, HTTP 5xx error rate > 5%, or data persistence unreachable. Response time: Immediate (< 5 mins).
- **P2 (High)**: Degraded performance, single replica failure with active pod disruption, elevated latency (> 1s). Response time: < 15 mins.
- **P3 (Medium)**: Non-critical internal tool issue or isolated transient error. Response time: < 2 hours.
- **P4 (Low)**: Minor cosmetic or configuration drift without customer impact. Response time: Next business day.

---

## 2. Standard Triage Workflow

```
[ Alertmanager Notification ]
              │
              ▼
    [ TITAN Incident Engine ]
  (Deterministic Rule Engine)
              │
      ┌───────┴───────┐
      ▼               ▼
[ Root Cause ]  [ Evidence Correlated ]
(Confidence %)   • Alert signals
                 • Probe status
                 • Recent deployment commits
              │
              ▼
  [ Allowlist Policy Gate ]
              │
       ┌──────┴──────┐
       ▼             ▼
 [ Safe Action ]  [ High-Risk Action ]
(Execute Auto)     (Requires Human Approval)
       │             │
       ▼             ▼
[ Post-Verification Probe ]
       │
       ▼
[ Resolved & Benchmarked ]
```

---

## 3. Playbooks by Incident Category

### Playbook 1: Bad Release (HTTP 500 Surge)
- **Signal**: `TitanHighErrorRate` firing, surge in HTTP 500 responses.
- **Verification**: Check recent deployment history in `services/platform-api` or Git commit history within last 15 minutes.
- **Remediation**:
  1. Trigger GitOps rollback via Argo CD or revert image tag in Kustomize overlay.
  2. If using TITAN CLI:
     ```bash
     python scripts/titan.py incident list
     ```
  3. Verify recovery via `/health/ready` and ensure 5xx rate drops to 0.

### Playbook 2: Database Dependency Outage
- **Signal**: `TitanDatabaseErrors` firing, readiness probe returning HTTP 503 while liveness remains 200.
- **Verification**: Check PostgreSQL RDS connectivity and connection pool metrics.
- **Remediation**:
  1. Inspect network policy and security group connectivity between EKS nodes and RDS.
  2. Verify credentials in AWS Secrets Manager or Vault.
  3. Restart connection pool if deadlocked.

### Playbook 3: Kubernetes Probe Deadlock
- **Signal**: Pods restarting in CrashLoopBackOff or isolated from endpoint slices.
- **Verification**: Inspect pod events:
  ```bash
  kubectl describe pod -l app=inventory-api -n titan-dev
  ```
- **Remediation**:
  1. Inspect CPU/memory limits or application event loop deadlocks.
  2. Adjust probe initialDelaySeconds if startup takes longer than timeout.

---

## 4. Post-Incident Review (PIR) Template

- **Incident ID**:
- **Date & Duration**:
- **Services Affected**:
- **Root Cause Summary**:
- **Timeline of Events (Detection, Diagnosis, Mitigation, Recovery)**:
- **Preventative Action Items**:
