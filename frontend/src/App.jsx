import { useState, useEffect } from 'react';
import Home from './pages/Home';
import Workspace from './pages/Workspace';
import Results from './pages/Results';
import Knowledge from './pages/Knowledge';
import Docs from './pages/Docs';
import SettingsPage from './pages/SettingsPage';
import Copilot from './pages/Copilot';
import { checkSystemHealth, analyzeIdea } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home', 'workspace', 'results', 'knowledge', 'docs', 'settings'
  const [systemHealth, setSystemHealth] = useState(null);
  const [patentData, setPatentData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [historyQueries, setHistoryQueries] = useState([]);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Custom user settings state
  const [userSettings, setUserSettings] = useState({
    apiKey: '',
    mockLLM: true,
    palette: 'indigo'
  });

  // Poll system health status every 10 seconds
  useEffect(() => {
    let active = true;
    
    async function getHealth() {
      const health = await checkSystemHealth();
      if (active) {
        setSystemHealth(health);
      }
    }

    getHealth();
    const interval = setInterval(getHealth, 10000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  // Apply visual theme color configurations from settings on startup
  useEffect(() => {
    const saved = localStorage.getItem('patentiq_settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setUserSettings(parsed);
        
        // Apply color palette property tokens to document element
        const palettes = {
          indigo: { primary: '#6366f1', light: '#818cf8', glow: 'rgba(99, 102, 241, 0.08)' },
          blue: { primary: '#2563eb', light: '#60a5fa', glow: 'rgba(37, 99, 235, 0.08)' },
          teal: { primary: '#0d9488', light: '#2dd4bf', glow: 'rgba(13, 148, 136, 0.08)' }
        };
        const p = palettes[parsed.palette || 'indigo'];
        if (p) {
          document.documentElement.style.setProperty('--primary', p.primary);
          document.documentElement.style.setProperty('--primary-light', p.light);
          document.documentElement.style.setProperty('--primary-glow', p.glow);
        }
      } catch (_) {}
    }
  }, []);

  const handleAnalyze = async ({ title, ideaText, topK, domainFilter, applicantFilter }) => {
    setIsAnalyzing(true);
    setErrorMsg(null);
    
    try {
      const data = await analyzeIdea({
        ideaText,
        topK,
        domainFilter,
        applicantFilter
      });
      
      setPatentData(data);
      
      // Save query run to local history list
      setHistoryQueries((prev) => [
        {
          id: Date.now(),
          title,
          query: ideaText,
          data
        },
        ...prev
      ]);

      setIsAnalyzing(false);
      // Automatically switch to dashboard results page
      setActiveTab('results');
    } catch (err) {
      console.error('Analysis failed:', err);
      setErrorMsg(err.message || 'An unexpected error occurred during pipeline execution.');
      setIsAnalyzing(false);
    }
  };

  const handleSelectHistoryItem = (item) => {
    setPatentData(item.data);
    setActiveTab('results');
  };

  const handleUpdateSettings = (settings) => {
    setUserSettings(settings);
    localStorage.setItem('patentiq_settings', JSON.stringify(settings));
  };

  // Health check helper for sidebar footer
  const getHealthBadge = () => {
    if (!systemHealth) return { text: 'Checking Status', color: 'var(--text-muted)' };
    if (systemHealth.status === 'healthy') return { text: 'System Online', color: 'var(--success)' };
    if (systemHealth.status === 'degraded') return { text: 'Degraded State', color: 'var(--warning)' };
    return { text: 'System Offline', color: 'var(--error)' };
  };

  const badge = getHealthBadge();

  const navItems = [
    { id: 'home', label: 'Home Overview', icon: '🏠' },
    { id: 'workspace', label: 'Research Workspace', icon: '💻' },
    { id: 'copilot', label: 'AI Research Copilot', icon: '🤖' },
    { id: 'results', label: 'Intelligence Center', icon: '📊' },
    { id: 'knowledge', label: 'Knowledge Ingestion', icon: '🧠' },
    { id: 'docs', label: 'Documentation', icon: '📖' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  return (
    <div className="app-container">
      {/* PERSISTENT LEFT SIDEBAR */}
      <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div>
          {/* Collapse Toggle trigger */}
          <div style={{ display: 'flex', justifyContent: sidebarCollapsed ? 'center' : 'flex-end', marginBottom: '12px' }}>
            <button 
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              style={{
                background: 'var(--bg-surface-secondary)',
                border: '1px solid var(--border-neutral)',
                color: 'var(--text-secondary)',
                borderRadius: 'var(--border-radius-sm)',
                cursor: 'pointer',
                fontSize: '12px',
                padding: '4px 8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all var(--transition-fast)'
              }}
              title={sidebarCollapsed ? 'Expand Menu' : 'Collapse Menu'}
            >
              {sidebarCollapsed ? '☰' : '✕'}
            </button>
          </div>

          {/* Logo Section */}
          <div className="sidebar-brand" style={{ paddingLeft: sidebarCollapsed ? '0' : '8px', justifyContent: sidebarCollapsed ? 'center' : 'flex-start' }}>
            <img 
              src="/logo.png" 
              style={{ 
                width: '32px', 
                height: '32px', 
                borderRadius: '6px', 
                objectFit: 'contain'
              }} 
              alt="πQ Logo" 
            />
            {!sidebarCollapsed && <span className="sidebar-logo-text">PatentIQ</span>}
          </div>

          {/* Navigation Links */}
          <nav className="sidebar-menu">
            {navItems.map((item) => (
              <button 
                key={item.id}
                className={`sidebar-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
                title={sidebarCollapsed ? item.label : ''}
                style={{
                  justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
                  padding: sidebarCollapsed ? '10px 0' : '10px 14px'
                }}
              >
                <span style={{ fontSize: '15px', marginRight: sidebarCollapsed ? '0' : '10px' }}>{item.icon}</span>
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </nav>
        </div>

        {/* Sidebar Footer Status Indicator */}
        <div className="sidebar-footer" style={{ padding: sidebarCollapsed ? '16px 0 0 0' : '16px 8px 0 8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-secondary)', justifyContent: sidebarCollapsed ? 'center' : 'flex-start' }}>
            <span style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: badge.color,
              display: 'inline-block'
            }} title={badge.text}></span>
            {!sidebarCollapsed && <span>{badge.text}</span>}
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT VIEWPORT */}
      <div className="main-viewport">
        {/* Global Error Banner */}
        {errorMsg && (
          <div className="container" style={{ marginTop: '20px' }}>
            <div 
              style={{ 
                background: 'rgba(239, 68, 68, 0.1)', 
                border: '1px solid var(--error)', 
                color: 'var(--text-primary)',
                padding: '12px 16px',
                borderRadius: 'var(--border-radius-md)',
                fontSize: '13px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <span><strong>Analysis Failure:</strong> {errorMsg}</span>
              <button 
                onClick={() => setErrorMsg(null)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  fontSize: '16px',
                  lineHeight: 1
                }}
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Routed views */}
        {activeTab === 'home' && (
          <Home onNavigate={setActiveTab} />
        )}
        {activeTab === 'copilot' && (
          <Copilot />
        )}
        {activeTab === 'workspace' && (
          <Workspace 
            onAnalyze={handleAnalyze} 
            isAnalyzing={isAnalyzing} 
            history={historyQueries}
            onSelectHistoryItem={handleSelectHistoryItem}
          />
        )}
        {activeTab === 'results' && (
          <Results 
            data={patentData} 
            onNavigate={setActiveTab} 
          />
        )}
        {activeTab === 'knowledge' && (
          <Knowledge systemHealth={systemHealth} />
        )}
        {activeTab === 'docs' && (
          <Docs />
        )}
        {activeTab === 'settings' && (
          <SettingsPage 
            userSettings={userSettings} 
            onUpdateSettings={handleUpdateSettings} 
          />
        )}
      </div>
    </div>
  );
}

export default App;
