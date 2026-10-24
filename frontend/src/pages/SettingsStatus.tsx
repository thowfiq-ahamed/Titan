import React from 'react';

export const SettingsStatus: React.FC = () => {
  const integrations = [
    { name: 'GitHub Actions CI', type: 'CI/CD & Security Gate', status: 'connected', detail: 'Lint, pytest, trivy, kustomize' },
    { name: 'GitHub Container Registry (GHCR)', type: 'Container Registry', status: 'connected', detail: 'Immutable image publishing' },
    { name: 'Prometheus & Alertmanager', type: 'Telemetry & Alerting', status: 'connected', detail: 'Webhook target :8002/api/v1/alerts' },
    { name: 'Grafana Dashboard', type: 'Observability UI', status: 'connected', detail: 'Auto-provisioned datasource' },
    { name: 'Argo CD', type: 'GitOps Controller', status: 'connected', detail: 'Application manifest reconciliation' },
    { name: 'AWS EKS & RDS (Terraform)', type: 'Cloud Infrastructure', status: 'ready', detail: 'Modules validated; pending approval' },
    { name: 'AWS OIDC Federation', type: 'IAM Least Privilege', status: 'ready', detail: 'Keyless GitHub Actions trust' },
    { name: 'Trivy Security Scanner', type: 'DevSecOps', status: 'connected', detail: 'Vulnerability gate in CI' },
    { name: 'HashiCorp Vault', type: 'Secrets Management', status: 'simulated', detail: 'Local dev policy configured' },
    { name: 'Splunk HEC Adapter', type: 'Security Audit Forwarder', status: 'simulated', detail: 'Safe fallback active' },
    { name: 'ELK Stack Logstash', type: 'Log Pipeline', status: 'optional', detail: 'TCP :5000 pipeline configured' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>Settings & Integration Status</h1>
        <p style={{ color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
          Verification status for all core and optional external platforms.
        </p>
      </div>

      <div className="card">
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '0.75rem 0' }}>INTEGRATION</th>
              <th>CATEGORY</th>
              <th>STATUS</th>
              <th>CONFIGURATION DETAILS</th>
            </tr>
          </thead>
          <tbody>
            {integrations.map((item, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #1f2937' }}>
                <td style={{ padding: '0.75rem 0', fontWeight: 600 }}>{item.name}</td>
                <td style={{ color: 'var(--text-muted)' }}>{item.type}</td>
                <td>
                  <span className={`badge ${item.status === 'connected' ? 'badge-success' : item.status === 'ready' ? 'badge-info' : 'badge-warning'}`}>
                    {item.status.toUpperCase()}
                  </span>
                </td>
                <td className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{item.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
