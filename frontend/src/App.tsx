import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Overview } from './pages/Overview';
import { ServiceCatalog } from './pages/ServiceCatalog';
import { IncidentCenter } from './pages/IncidentCenter';
import { ReliabilityLab } from './pages/ReliabilityLab';
import { BenchmarkReports } from './pages/BenchmarkReports';
import { DeploymentHistory } from './pages/DeploymentHistory';
import { SettingsStatus } from './pages/SettingsStatus';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState('overview');

  const renderPage = () => {
    switch (currentPage) {
      case 'overview': return <Overview />;
      case 'catalog': return <ServiceCatalog />;
      case 'incidents': return <IncidentCenter />;
      case 'lab': return <ReliabilityLab />;
      case 'benchmarks': return <BenchmarkReports />;
      case 'deployments': return <DeploymentHistory />;
      case 'settings': return <SettingsStatus />;
      default: return <Overview />;
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar currentPage={currentPage} onPageChange={setCurrentPage} />
      <main style={{ flex: 1, maxWidth: '1400px', width: '100%', margin: '0 auto', padding: '2rem' }}>
        {renderPage()}
      </main>
      <footer style={{ borderTop: '1px solid var(--border)', padding: '1rem 2rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        TITAN Platform Engineering & Reliability Intelligence • Cloud-Native Monorepo Portfolio
      </footer>
    </div>
  );
};

export default App;
