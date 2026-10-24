# TITAN Platform: GitHub Repository Setup & Safe Publication Guide

This guide details the procedure for connecting and publishing the TITAN platform repository to GitHub with strict security controls.

---

## 1. Pre-Publication Security & Hygiene Audit

Before pushing to any remote repository, verify that no sensitive files are tracked:

```powershell
# Check current Git status
git status

# Verify .gitignore enforces exclusion of credentials, virtualenvs, and state
git check-ignore -v .env
git check-ignore -v .venv/
git check-ignore -v terraform/environments/dev/terraform.tfstate
```

Ensure only clean source code, configurations, and documentation are staged.

---

## 2. GitHub Repository Creation

1. Log in to [GitHub](https://github.com).
2. Click **New Repository**.
3. Settings:
   - **Repository name**: `titan` (or `titan-platform`)
   - **Description**: `Cloud-Native Delivery, Platform Engineering & Reliability Intelligence Platform`
   - **Visibility**: `Public` (recommended for portfolio) or `Private`
   - **Initialize with**: Leave *README*, *.gitignore*, and *license* UNCHECKED (since our workspace already contains them).

---

## 3. Connecting Local Workspace to Remote

```powershell
# 1. Review and stage all project files
git add .

# 2. Create the initial foundational commit
git commit -m "feat: initial commit of TITAN Cloud-Native Delivery & Reliability Platform"

# 3. Rename branch to standard 'main'
git branch -M main

# 4. Add your GitHub remote (replace with your actual username)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/titan.git

# 5. Push initial commit (Requires explicit user confirmation)
git push -u origin main
```

---

## 4. Configuring Branch Protections

In GitHub under **Settings > Branches**:
- Click **Add branch protection rule** for `main`.
- Require a pull request before merging.
- Require status checks to pass before merging:
  - `test (Test & Code Quality Gate)`
  - `manifest-validation (Validate Kubernetes & Kustomize Manifests)`
- Include administrators in restrictions.
