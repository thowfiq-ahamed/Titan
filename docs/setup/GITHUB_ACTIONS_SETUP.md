# TITAN Platform: GitHub Actions & Automation Setup

This guide details the CI/CD pipeline automation, least-privilege permissions, security gates, and AWS OIDC keyless authentication.

---

## 1. Automated Workflow Pipeline Architecture

TITAN implements two primary workflows in `.github/workflows/`:

1. **`ci.yaml` (PR & Push Validation Gate)**:
   - **Quality Stage**: Runs `ruff` linter and executes 33+ automated unit/API/integration tests using `pytest` with coverage report generation.
   - **Manifest Validation Stage**: Builds and validates Kubernetes Kustomize manifests across `dev`, `staging`, and `prod` overlays.
   - **DevSecOps Security Stage**: Builds the container image and scans with `trivy` for `CRITICAL` and `HIGH` CVEs.
2. **`release-gitops.yaml` (Release & GitOps Sync)**:
   - Publishes hardened container image to GitHub Container Registry (GHCR) using immutable commit tags (`sha-<7char>`).
   - Updates the Kustomize overlay in Git with the new immutable tag.
   - Triggers automated Argo CD GitOps reconciliation.

---

## 2. Keyless AWS OIDC Authentication Setup

TITAN avoids permanent, long-lived AWS IAM Access Keys by utilizing OpenID Connect (OIDC) identity federation:

1. In AWS IAM, an Identity Provider `token.actions.githubusercontent.com` is configured via `terraform/modules/iam`.
2. An IAM Role `titan-github-actions-oidc-dev` is created with trust policy bound strictly to `repo:your-org/titan:*`.
3. In GitHub Actions, the workflow requests temporary, short-lived STS credentials:

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - name: Configure AWS Credentials via OIDC
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/titan-github-actions-oidc-dev
      aws-region: us-east-1
```

---

## 3. Diagnosing Pipeline Failures

- **Test Failures**: Inspect the `Execute Automated Test Suite` step in the Actions tab. Full pytest failure logs and stack traces are captured.
- **Trivy CVE Rejections**: Review the security summary table in the workflow run. Trivy identifies the vulnerable package, installed version, and fixed version.
- **Kustomize Compile Errors**: Check `kubectl kustomize` output locally before committing:
  ```powershell
  kubectl kustomize deploy/kustomize/overlays/dev
  ```
