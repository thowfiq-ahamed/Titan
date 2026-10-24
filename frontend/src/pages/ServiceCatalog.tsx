import React, { useState, useEffect } from 'react';
import { fetchServices, ServiceItem } from '../api/client';

export const ServiceCatalog: React.FC = () => {
  const [services, setServices] = useState<ServiceItem[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDisplay, setNewDisplay] = useState('');
  const [newTier, setNewTier] = useState('tier-1');

  useEffect(() => {
    fetchServices().then(setServices);
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName) return;
    try {
      const res = await fetch('/api/v1/services', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Titan-API-Key': 'titan-platform-master-key-2026'
        },
        body: JSON.stringify({
          name: newName,
          display_name: newDisplay || newName,
          tier: newTier,
          owner_team: 'platform-engineering'
        })
      });
      if (res.ok) {
        setShowModal(false);
        setNewName('');
        setNewDisplay('');
        fetchServices().then(setServices);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>Service Catalog</h1>
          <p style={{ color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
            Standardized microservice directory with deployment policies and telemetry specifications.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + Register New Service
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1rem' }}>
        {services.map((s) => (
          <div key={s.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>{s.display_name}</h3>
                <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.name}</span>
              </div>
              <span className="badge badge-info">{s.tier}</span>
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', margin: 0 }}>{s.description}</p>
            <div style={{ borderTop: '1px solid var(--border)', paddingTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.8rem' }}>
              <div><strong>Team:</strong> <span style={{ color: 'var(--text-muted)' }}>{s.owner_team}</span></div>
              <div><strong>Probe:</strong> <span className="mono" style={{ color: '#38bdf8' }}>{s.health_endpoint}</span></div>
              <div><strong>Metrics:</strong> <span className="mono" style={{ color: '#34d399' }}>{s.metrics_endpoint}</span></div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
          <div className="card" style={{ width: '450px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>
            <h2 style={{ marginTop: 0 }}>Register Microservice</h2>
            <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.25rem' }}>Service Identifier (k8s name)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. order-service"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'white' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.25rem' }}>Display Name</label>
                <input
                  type="text"
                  placeholder="Order Processing Service"
                  value={newDisplay}
                  onChange={(e) => setNewDisplay(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'white' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.25rem' }}>Service Tier</label>
                <select
                  value={newTier}
                  onChange={(e) => setNewTier(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'white' }}
                >
                  <option value="tier-0">Tier 0 (Mission Critical)</option>
                  <option value="tier-1">Tier 1 (Core Business)</option>
                  <option value="tier-2">Tier 2 (Internal)</option>
                </select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1rem' }}>
                <button type="button" className="btn" style={{ background: 'var(--border)', color: 'white' }} onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Register Service
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
