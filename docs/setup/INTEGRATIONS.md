# TITAN Platform: External Platform Integrations Guide

This document specifies the architecture, setup procedure, authentication, and verification for each external service integrated into TITAN.

---

## Integration Matrix

| Integration | Classification | Purpose | Primary Location |
|---|---|---|---|
| **GitHub** | Core | Source control, PR automation, issue tracking | Root repository |
| **GitHub Actions** | Core | Primary CI/CD automation & security gating | `.github/workflows/` |
| **GHCR** | Core | Primary OCI container image registry | Container publication |
| **Amazon ECR** | Optional / Cloud | AWS private container registry with scan-on-push | `terraform/modules/ecr` |
| **Kubernetes (kind / Minikube)** | Core | Local cluster orchestration & probe testing | `deploy/kustomize/` |
| **AWS (EKS, RDS, VPC)** | Optional / Cloud | Scalable cloud deployment | `terraform/environments/` |
| **Argo CD** | Core | Primary GitOps controller & automated self-healing | `gitops/argocd/` |
| **Flux CD** | Optional / Demo | Isolated GitOps comparison environment | `gitops/flux/` |
| **Prometheus & Alertmanager** | Core | Metrics scraping & incident trigger webhooks | `observability/prometheus/` |
| **Grafana** | Core | Observability & Golden Signal visualization | `observability/grafana/` |
| **ELK Stack** | Optional | Centralized structured log ingestion & search | `observability/elastic/` |
| **Splunk** | Optional | Security audit event delivery via HEC | `observability/splunk/` |
| **Trivy** | Core | Container CVE vulnerability scanning | `security/trivy/` |
| **HashiCorp Vault** | Optional | Dynamic secret management & lease governance | `security/vault/` |
| **Jenkins** | Optional | Alternate declarative CI pipeline demonstration | `ci/jenkins/` |

---

## 1. Container Registries: GHCR & Amazon ECR

### GitHub Container Registry (GHCR)
- **Authentication**: Uses `${{ secrets.GITHUB_TOKEN }}` in CI.
- **Local Login**:
  ```bash
  echo $CR_PAT | docker login ghcr.io -u <YOUR_USERNAME> --password-stdin
  ```
- **Tagging Format**: `ghcr.io/<ORG>/titan-inventory-api:sha-<COMMIT_SHA>`

### Amazon ECR
- **Authentication**: Authenticate via AWS CLI:
  ```bash
  aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
  ```
- **Security**: Tag immutability enforced; scan-on-push active.

---

## 2. Local Kubernetes (kind / Minikube)

### Creating a Local kind Cluster with Ingress Port Mappings
```bash
kind create cluster --name titan-cluster --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF
```

### Deploying the Workload via Kustomize
```bash
kubectl apply -k deploy/kustomize/overlays/dev
kubectl get pods -n titan-dev -w
```

---

## 3. Argo CD Setup & Sync

1. Install Argo CD:
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```
2. Deploy TITAN Applications:
   ```bash
   kubectl apply -f gitops/argocd/application-dev.yaml
   ```
3. Verify GitOps Sync:
   ```bash
   kubectl get application -n argocd titan-inventory-dev
   ```

---

## 4. Observability: Prometheus, Alertmanager, Grafana

- **Scrape Configuration**: Configured in `observability/prometheus/prometheus.yml` pointing to workload endpoints `/metrics`.
- **Alert Rules**: Rules in `alert_rules.yml` evaluate golden signals (e.g. `TitanHighErrorRate`).
- **Webhook Route**: Alertmanager sends HTTP POST to `http://incident-engine:8002/api/v1/alerts`.
- **Local Verification**:
  ```bash
  curl http://localhost:8001/metrics
  ```

---

## 5. Security Scanning: Trivy & Vault

### Trivy Container Vulnerability Scan
```bash
trivy image --severity HIGH,CRITICAL titan-inventory-api:v1.0.0
```

### HashiCorp Vault Demonstration
```bash
# Start local Vault in development mode
vault server -dev -dev-root-token-id="root"

# Apply policy
vault policy write titan-policy security/vault/titan-policy.hcl

# Store database secret
vault kv put secret/titan/inventory-api/database password="super_secure_vault_password"
```

---

## 6. Splunk Event Collector (HEC)

- Configuration: Set `SPLUNK_HEC_URL` and `SPLUNK_HEC_TOKEN` in `.env`.
- If unconfigured, `observability/splunk/splunk_adapter.py` safely logs audit events locally without errors (Rule 9).
