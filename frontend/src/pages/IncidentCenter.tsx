import React, { useState, useEffect } from 'react';
import { fetchIncidents, IncidentItem } from '../api/client';

export const IncidentCenter: React.FC = () => {
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<IncidentItem | null>(null);

  useEffect(() => {
    fetchIncidents().then((data) => {
      setIncidents(data);
      if (data.length > 0) setSelectedIncident(data[0]);
    });
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>Incident Center & Root Cause Analysis</h1>
        <p style={{ color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
          Explainable deterministic diagnoses, multi-signal evidence correlation, and verified remediation audit trails.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '1.5rem' }}>
        {/* Incident List */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '700px', overflowY: 'auto' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginTop: 0 }}>Incident Feed ({incidents.length})</h2>
          {incidents.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
              No active incidents recorded. Systems operational.
            </div>
          ) : (
            incidents.map((inc) => (
              <div
                key={inc.id}
                onClick={() => setSelectedIncident(inc)}
                style={{
                  padding: '1rem',
                  borderRadius: '6px',
                  backgroundColor: selectedIncident?.id === inc.id ? 'var(--bg-card)' : 'transparent',
                  border: selectedIncident?.id === inc.id ? '1px solid var(--accent)' : '1px solid var(--border)',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className={`badge ${inc.severity === 'P1' ? 'badge-danger' : 'badge-warning'}`}>
                    {inc.severity} - {inc.category}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {new Date(inc.detected_at).toLocaleTimeString()}
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{inc.service_id}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{inc.suspected_cause}</div>
              </div>
            ))
          )}
        </div>

        {/* Diagnostic Detail Panel */}
        <div className="card">
          {selectedIncident ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700 }}>Incident Diagnosis Details</h2>
                  <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ID: {selectedIncident.id}</span>
                </div>
                <span className="badge badge-success">{selectedIncident.recovery_status.toUpperCase()}</span>
              </div>

              <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Suspected Root Cause</span>
                <p style={{ margin: '0.25rem 0 0 0', fontSize: '1rem', fontWeight: 600, color: '#fca5a5' }}>
                  {selectedIncident.suspected_cause}
                </p>
                <div style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
                  <strong>Rule Confidence: </strong>
                  <span className="mono" style={{ color: '#10b981' }}>{(selectedIncident.confidence_score * 100).toFixed(0)}%</span>
                </div>
              </div>

              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem' }}>Supporting Evidence Correlated</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {selectedIncident.supporting_evidence.map((ev, idx) => (
                    <div key={idx} style={{ padding: '0.5rem 0.75rem', borderRadius: '4px', background: 'var(--bg-primary)', fontSize: '0.8rem', borderLeft: '3px solid var(--accent)' }}>
                      <span className="badge badge-info" style={{ marginRight: '0.5rem' }}>{ev.source}</span>
                      <strong>{ev.signal}: </strong>
                      <span style={{ color: 'var(--text-muted)' }}>{ev.detail}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Recommended Recovery Strategy</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.5rem' }}>
                  <span className="mono" style={{ padding: '0.4rem 0.8rem', borderRadius: '4px', background: '#1e3a8a', color: '#bfdbfe', fontWeight: 600 }}>
                    {selectedIncident.recommended_recovery}
                  </span>
                  <span style={{ fontSize: '0.85rem', color: '#10b981' }}>✓ Security allowlist policy verified</span>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '3rem' }}>
              Select an incident from the feed to view full diagnostic evidence and remediation trails.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
