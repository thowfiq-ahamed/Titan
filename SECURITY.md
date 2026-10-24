# Security Policy: TITAN Platform

## Security Philosophy & DevSecOps Controls

TITAN is designed from the ground up with a Defense-in-Depth posture across software supply chain, container runtime, Kubernetes clustering, and cloud infrastructure:

1. **Least Privilege by Default**: Services run as unprivileged users (UID 10001 `appuser`), non-root, with read-only root filesystems where applicable and `allowPrivilegeEscalation: false`.
2. **Secret Hygiene**: Zero hardcoded credentials. All configuration is injected via environment variables or secret managers (HashiCorp Vault / Kubernetes Secrets). `.env` files and `.tfstate` files are strictly gitignored.
3. **Controlled Reliability Lab Safety**: Fault-injection mechanisms are strictly guarded behind environment flags (`ENABLE_FAULT_INJECTION=true`) and API authorization. In production environments, fault injection endpoints return HTTP 403 Forbidden or are not mounted.
4. **Supply Chain Security**: Container images are scanned with Trivy in CI pipelines. Prohibited critical and high CVEs block release publication. Base images are pinned to minimal, verified distroless/slim distributions.
5. **No Blind Command Execution**: The Incident Engine only executes allowlisted, deterministic remediation actions. Alert payloads, metrics, and logs are never fed to shell execution contexts.

## Reporting a Vulnerability

If you discover a security issue or vulnerability within this project, please follow safe disclosure practices:
- Do not open a public issue on GitHub.
- Submit details privately to the project maintainers.
- Provide a reproducible demonstration of the issue, affected components, and potential impact.
- Maintainers will triage and provide a patch within a coordinated timeframe.
