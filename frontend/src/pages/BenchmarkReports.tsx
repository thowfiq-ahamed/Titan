import React, { useState, useEffect } from 'react';
import { fetchBenchmarkSummary, BenchmarkSummaryData } from '../api/client';
import { MetricCard } from '../components/MetricCard';

export const BenchmarkReports: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<BenchmarkSummaryData | null>(null);

  useEffect(() => {
    fetchBenchmarkSummary().then(setBenchmarks);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>Reliability Benchmark Reports</h1>
        <p style={{ color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
          Quantitative resilience metrics, empirical recovery timelines, and recovery strategy comparisons.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        <MetricCard
          title="Total Controlled Trials"
          value={benchmarks?.total_experiments ?? 0}
          subtext="Executed across scenarios"
        />
        <MetricCard
          title="Mean Time To Detect (MTTD)"
          value={`${benchmarks?.mean_time_to_detect_seconds ?? 0}s`}
          subtext="From fault to Alertmanager signal"
          status="info"
        />
        <MetricCard
          title="Mean Time To Diagnose"
          value={`${benchmarks?.mean_time_to_diagnose_seconds ?? 0}s`}
          subtext="Deterministic RCA duration"
          status="info"
        />
        <MetricCard
          title="Mean Time To Recover (MTTR)"
          value={`${benchmarks?.mean_time_to_recover_seconds ?? 0}s`}
          subtext="From detection to verified healthy"
          status="success"
        />
      </div>

      <div className="card">
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginTop: 0 }}>Recovery Strategy Performance Comparison</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '0.75rem 0' }}>RECOVERY STRATEGY</th>
              <th>TRIALS CONDUCTED</th>
              <th>SUCCESS RATE</th>
              <th>AVERAGE RECOVERY TIME</th>
              <th>EVALUATION</th>
            </tr>
          </thead>
          <tbody>
            {benchmarks && Object.entries(benchmarks.strategy_breakdown).map(([strategy, data]) => (
              <tr key={strategy} style={{ borderBottom: '1px solid #1f2937' }}>
                <td style={{ padding: '0.75rem 0', fontWeight: 600 }} className="mono">{strategy}</td>
                <td>{data.trials} runs</td>
                <td><span className="badge badge-success">{data.success_rate_pct}%</span></td>
                <td className="mono" style={{ color: '#38bdf8' }}>{data.mean_recovery_sec} seconds</td>
                <td>
                  <span style={{ color: 'var(--text-muted)' }}>
                    {strategy === 'app_rollback' ? 'Fastest for bad release rollouts' :
                     strategy === 'policy_recovery' ? 'Optimal for dependency reconnection' :
                     'Standard container restart loop'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
