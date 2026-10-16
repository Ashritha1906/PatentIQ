import React from 'react';
import Logo from './Logo';

export default function Header({ systemHealth }) {
  const getStatusDetails = () => {
    if (!systemHealth) {
      return { text: 'Checking Status...', className: '' };
    }
    if (systemHealth.status === 'healthy') {
      return { text: `Online - DB ${systemHealth.database || 'connected'}`, className: 'online' };
    }
    if (systemHealth.status === 'degraded') {
      return { text: 'Degraded', className: 'warning' };
    }
    return { text: 'Offline', className: 'offline' };
  };

  const status = getStatusDetails();

  return (
    <header className="main-header">
      <div className="container header-container">
        <div className="logo-section">
          <Logo size={28} />
        </div>
        
        <div className="status-badge" title={`Database Status: ${systemHealth?.database || 'Unknown'}\nLLM Mode: ${systemHealth?.llm_mode || 'Unknown'}`}>
          <span className={`status-indicator ${status.className}`} style={
            status.className === 'warning' ? { backgroundColor: 'var(--warning)' } : {}
          }></span>
          <span>{status.text}</span>
        </div>
      </div>
    </header>
  );
}
