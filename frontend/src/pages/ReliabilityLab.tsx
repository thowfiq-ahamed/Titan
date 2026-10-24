import React, { useState } from 'react';
import { triggerFaultInjection, resetAllFaults } from '../api/client';

export const ReliabilityLab: React.FC = () => {
  const [activeFault, setActiveFault] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('Ready for controlled experimentation.');
  const [confirmModal, setConfirmModal] = useState<string | null>(null);
  const [running, setRunning] = useState<boolean>(false);

  const scenarios = [
    {
      id: 'SCN-001',
      title: 'Broken Release (HTTP 500 Surge)',
      description: 'Simulates corrupted application release deployment that throws immediate 500 errors on API routes.',
      expectedSignal: 'TitanHighErrorRate firing on Alertmanager',
      recoveryStrategy: 'app_rollback'
    },
    {
      id: 'SCN-002',
      title: 'Kubernetes Probe Deadlock',
      description: 'Simulates liveness/readiness probe failure causing service removal from endpoints or container restart.',
      expectedSignal: 'Readiness probe 503 / Endpoint slice drained',
      recoveryStrategy: 'k8s_self_heal'
    },
    {
      id: 'SCN-003',
      title: 'PostgreSQL Dependency Outage',
      description: 'Simulates database disconnection while keeping container process running.',
      expectedSignal: 'TitanDatabaseErrors active / Readiness failure',
      recoveryStrategy: 'policy_recovery'
    }
  ];

  const executeFault = async (scenarioId: string) => {
    setRunning(true);
    setStatusMessage(`Injecting controlled fault for ${scenarioId}...`);
    try {
      await triggerFaultInjection(scenarioId);
      setActiveFault(scenarioId);
      setStatusMessage(`Fault ${scenarioId} injected successfully. Telemetry and Incident Engine monitoring active.`);
    } catch (err) {
      setStatusMessage(`Error injecting fault: ${err}`);
    } finally {
      setRunning(false);
      setConfirmModal(null);
    }
  };

  const handleReset = async () => {
    setRunning(true);
    setStatusMessage('Executing automated recovery and resetting all simulated faults...');
    try {
      await resetAllFaults();
      setActiveFault(null);
      setStatusMessage('Healthy baseline restored. All probes and API endpoints operating normally.');
    } catch (err) {
      setStatusMessage(`Error resetting baseline: ${err}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>TITAN Reliability Lab</h1>
          <p style={{ color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
            Controlled chaos & resilience engineering testbed. Injects bounded failures to measure empirical recovery efficiency.
          </p>
        </div>
        <button
          className="btn btn-danger"
          onClick={handleReset}
          disabled={running}
          style={{ background: '#059669', borderColor: '#10b981', color: 'white' }}
        >
          ↺ Reset Baseline to Healthy
        </button>
      </div>

      <div className="card" style={{ backgroundColor: 'var(--bg-primary)', borderLeft: '4px solid var(--accent)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <strong>Laboratory Status: </strong>
            <span style={{ color: activeFault ? '#f87171' : '#34d399', fontWeight: 600 }}>
              {activeFault ? `SIMULATING FAULT (${activeFault})` : 'BASELINE HEALTHY'}
            </span>
          </div>
          <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{statusMessage}</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem' }}>
        {scenarios.map((scn) => (
          <div key={scn.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <span className="badge badge-info">{scn.id}</span>
              <span className="mono" style={{ fontSize: '0.75rem', color: '#10b981' }}>strategy: {scn.recoveryStrategy}</span>
            </div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>{scn.title}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>{scn.description}</p>
            <div style={{ borderTop: '1px solid var(--border)', paddingTop: '0.75rem', fontSize: '0.8rem' }}>
              <strong>Expected Signal: </strong>
              <span className="mono" style={{ color: '#f59e0b' }}>{scn.expectedSignal}</span>
            </div>
            <button
              className="btn btn-danger"
              style={{ marginTop: 'auto' }}
              onClick={() => setConfirmModal(scn.id)}
              disabled={running}
            >
              ⚡ Inject Controlled Failure
            </button>
          </div>
        ))}
      </div>

      {confirmModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
          <div className="card" style={{ width: '450px', backgroundColor: 'var(--bg-secondary)', border: '1px solid #dc2626' }}>
            <h2 style={{ marginTop: 0, color: '#f87171' }}>Confirm Fault Injection</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              Are you sure you want to introduce controlled failure <strong>{confirmModal}</strong> into the target test environment?
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1.5rem' }}>
              <button className="btn" style={{ background: 'var(--border)', color: 'white' }} onClick={() => setConfirmModal(null)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={() => executeFault(confirmModal)}>
                Confirm & Inject
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
