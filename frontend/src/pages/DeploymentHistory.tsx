import React from 'react';

export const DeploymentHistory: React.FC = () => {
  const deployments = [
    {
      id: 'dep-101',
      service: 'inventory-api',
      environment: 'dev',
      imageTag: 'sha-e89a3f2',
      commit: 'e89a3f2',
      gitopsSynced: true,
      replicas: '1/1',
      status: 'healthy',
      time: '10 mins ago'
    },
    {
      id: 'dep-100',
      service: 'inventory-api',
      environment: 'staging',
      imageTag: 'sha-b41c09d',
      commit: 'b41c09d',
      gitopsSynced: true,
      replicas: '2/2',
      status: 'healthy',
      time: '1 hour ago'
    },
    {
      id: 'dep-099',
      service: 'inventory-api',
      environment: 'prod',
      imageTag: 'v1.0.0',
      commit: 'a12f788',
      gitopsSynced: true,
      replicas: '4/4',
      status: 'healthy',
      time: '1 day ago'
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>Deployment History & GitOps Status</h1>
        <p style={{ color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
          Immutable image release tracking, commit provenance, and Argo CD desired-state reconciliation.
        </p>
      </div>

      <div className="card">
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '0.75rem 0' }}>DEPLOYMENT ID</th>
              <th>SERVICE</th>
              <th>ENV</th>
              <th>IMMUTABLE TAG</th>
              <th>GITOPS SYNC</th>
              <th>REPLICAS</th>
              <th>STATUS</th>
              <th>TIME</th>
            </tr>
          </thead>
          <tbody>
            {deployments.map((d) => (
              <tr key={d.id} style={{ borderBottom: '1px solid #1f2937' }}>
                <td style={{ padding: '0.75rem 0' }} className="mono">{d.id}</td>
                <td style={{ fontWeight: 600 }}>{d.service}</td>
                <td><span className="badge badge-info">{d.environment}</span></td>
                <td className="mono" style={{ color: '#38bdf8' }}>{d.imageTag}</td>
                <td><span className="badge badge-success">SYNCED (ARGO CD)</span></td>
                <td className="mono">{d.replicas}</td>
                <td><span className="badge badge-success">{d.status.toUpperCase()}</span></td>
                <td style={{ color: 'var(--text-muted)' }}>{d.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
