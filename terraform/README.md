# TITAN Cloud Infrastructure (AWS & Terraform)

## 1. Modular Architecture Overview

TITAN uses modular Terraform code with environment separation:

- `terraform/bootstrap/`: Creates S3 bucket with AES256 server-side encryption, versioning, and DynamoDB state locking table without circular dependencies.
- `terraform/modules/`:
  - `vpc`: 3-tier networking (Public, Private App, Private DB), Internet Gateway, NAT Gateway.
  - `security_groups`: Least-privilege ingress/egress. RDS PostgreSQL strictly restricts port 5432 ingress solely to EKS worker node security groups.
  - `iam`: EKS cluster and node roles, plus GitHub Actions OIDC federation role for keyless CI/CD authentication.
  - `ecr`: Private container repository with immutable tags, scan-on-push, and lifecycle retention policies.
  - `eks`: Managed Kubernetes cluster (v1.30+) with managed node groups and CloudWatch audit logging.
  - `rds`: PostgreSQL 16 Multi-AZ database across private database subnets with KMS-encrypted storage and credentials in AWS Secrets Manager.
- `terraform/environments/`: Separate configurations for `dev` and `staging`.

---

## 2. Monthly Cost Estimates (US-East-1)

| Resource | Configuration | Estimated Cost / Month |
|---|---|---|
| **EKS Control Plane** | 1 Cluster | ~$73.00 |
| **EKS Worker Nodes** | 2x `t3.medium` instances | ~$60.00 |
| **NAT Gateway** | 1 Single NAT Gateway (Dev) | ~$32.40 + data transfer |
| **RDS PostgreSQL** | 1x `db.t4g.micro` (Single-AZ dev) | ~$12.50 |
| **EBS Storage** | 40 GB gp3 | ~$3.20 |
| **ECR & S3 State** | Repositories & state storage | ~$1.00 |
| **Total Estimated Dev** | Minimal resilient topology | **~$182.10 / month** |

> [!IMPORTANT]
> **Safety Rule 13**: Do not provision paid AWS resources, run destructive Terraform operations, or deploy publicly accessible infrastructure without explicit user approval.

---

## 3. Remote State Bootstrap Sequence

To provision remote state for the first time:

```bash
cd terraform/bootstrap
terraform init
terraform apply
```

Note the output S3 bucket name and DynamoDB table. Then uncomment the `backend "s3"` block in `terraform/environments/dev/versions.tf` and run:

```bash
cd terraform/environments/dev
terraform init -backend-config="bucket=titan-terraform-state-us-east-1"
```

---

## 4. Teardown & Resource Cleanup

To safely tear down all provisioned cloud infrastructure and stop billing:

```bash
cd terraform/environments/dev
terraform destroy -auto-approve
```
