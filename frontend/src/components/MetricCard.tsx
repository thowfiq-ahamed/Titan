import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  status?: 'success' | 'warning' | 'danger' | 'info';
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtext, status = 'info' }) => {
  const getBorderColor = () => {
    switch (status) {
      case 'success': return 'var(--success)';
      case 'warning': return 'var(--warning)';
      case 'danger': return 'var(--danger)';
      default: return 'var(--accent)';
    }
  };

  return (
    <div className="card" style={{ borderLeft: `4px solid ${getBorderColor()}`, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>{title}</span>
      <span style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'JetBrains Mono, monospace' }}>{value}</span>
      {subtext && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{subtext}</span>}
    </div>
  );
};
