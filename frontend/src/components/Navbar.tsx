import React from 'react';

interface NavbarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPage, onPageChange }) => {
  const navItems = [
    { id: 'overview', label: 'Overview' },
    { id: 'catalog', label: 'Service Catalog' },
    { id: 'incidents', label: 'Incident Center' },
    { id: 'lab', label: 'Reliability Lab' },
    { id: 'benchmarks', label: 'Benchmark Reports' },
    { id: 'deployments', label: 'Deployments' },
    { id: 'settings', label: 'Settings & Status' }
  ];

  return (
    <header style={{ borderBottom: '1px solid var(--border)', backgroundColor: 'var(--bg-secondary)', padding: '0.75rem 2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', cursor: 'pointer' }} onClick={() => onPageChange('overview')}>
          <div style={{ width: '32px', height: '32px', borderRadius: '6px', backgroundColor: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
            T
          </div>
          <span style={{ fontSize: '1.25rem', fontWeight: 'bold', letterSpacing: '0.05em' }}>TITAN</span>
          <span className="badge badge-info" style={{ marginLeft: '0.5rem' }}>Platform Eng & SRE</span>
        </div>

        <nav style={{ display: 'flex', gap: '0.5rem' }}>
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              style={{
                background: currentPage === item.id ? 'var(--bg-card)' : 'transparent',
                color: currentPage === item.id ? 'var(--accent)' : 'var(--text-muted)',
                border: 'none',
                borderRadius: '6px',
                padding: '0.5rem 0.85rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
};
