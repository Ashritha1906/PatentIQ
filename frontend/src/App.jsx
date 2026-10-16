import React, { useState, useEffect } from 'react';
import Home from './pages/Home';
import Workspace from './pages/Workspace';
import Results from './pages/Results';
import Knowledge from './pages/Knowledge';
import Docs from './pages/Docs';
import SettingsPage from './pages/SettingsPage';
import Copilot from './pages/Copilot';
import PatentComparison from './pages/PatentComparison';
import InnovationRefinement from './pages/InnovationRefinement';
import ReportWorkspace from './pages/ReportWorkspace';
import { Icon } from './components/Icons';
import { checkSystemHealth, analyzeIdea } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [initialWorkspaceQuery, setInitialWorkspaceQuery] = useState('');
  // Theme Management (Dark / Light)
  const [theme, setTheme] = useState(() => localStorage.getItem('patentiq_theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('patentiq_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const [systemHealth, setSystemHealth] = useState(null);
  const [patentData, setPatentData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [historyQueries, setHistoryQueries] = useState([]);
  const [comparisonPatents, setComparisonPatents] = useState([]);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  const [userSettings, setUserSettings] = useState({
    apiKey: '',
    mockLLM: true,
    palette: 'indigo'
  });

  // Poll system health status every 12 seconds
  useEffect(() => {
    let active = true;
    
    async function getHealth() {
      const health = await checkSystemHealth();
      if (active) {
        setSystemHealth(health);
      }
    }

    getHealth();
    const interval = setInterval(getHealth, 12000);

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
      } catch {}
    }
  }, []);

  const handleNavigate = (tab, query = '') => {
    if (query) {
      setInitialWorkspaceQuery(query);
    }
    setActiveTab(tab);
  };

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
      setActiveTab('results');
    } catch (err) {
      console.error('Analysis failed:', err);
      setErrorMsg(err.message || 'An unexpected error occurred during pipeline execution.');
      setIsAnalyzing(false);
    }
  };

  const handleStartComparison = (patents) => {
    setComparisonPatents(patents);
    setActiveTab('compare');
  };

  const handleSelectHistoryItem = (item) => {
    setPatentData(item.data);
    setActiveTab('results');
  };

  const handleUpdateSettings = (settings) => {
    setUserSettings(settings);
    localStorage.setItem('patentiq_settings', JSON.stringify(settings));
  };

  const getHealthBadge = () => {
    if (!systemHealth) return { text: 'Checking Status', statusClass: 'offline' };
    if (systemHealth.status === 'healthy') return { text: 'System Online', statusClass: 'online' };
    if (systemHealth.status === 'degraded') return { text: 'Degraded State', statusClass: 'degraded' };
    return { text: 'System Offline', statusClass: 'offline' };
  };

  const badge = getHealthBadge();

  const primaryNavItems = [
    { id: 'home', label: 'Overview', icon: 'home' },
    { id: 'workspace', label: 'Patent Search', icon: 'search' },
    { id: 'copilot', label: 'AI Copilot', icon: 'copilot' },
    { id: 'compare', label: 'Patent Comparison', icon: 'compare' },
    { id: 'innovation', label: 'Innovation Refinement', icon: 'innovation' },
    { id: 'reports', label: 'Research Reports', icon: 'reports' },
    { id: 'results', label: 'Intelligence Center', icon: 'results' }
  ];

  const secondaryNavItems = [
    { id: 'knowledge', label: 'Knowledge Ingestion', icon: 'knowledge' },
    { id: 'docs', label: 'Documentation', icon: 'docs' },
    { id: 'settings', label: 'Settings', icon: 'settings' }
  ];

  const getPageTitle = (tab) => {
    switch (tab) {
      case 'home': return { title: 'Overview', desc: 'Enterprise AI patent intelligence and prior-art discovery' };
      case 'workspace': return { title: 'Patent Search', desc: 'Natural language semantic & hybrid prior-art retrieval' };
      case 'copilot': return { title: 'AI Research Copilot', desc: 'Conversational prior-art exploration, claims inquiry & voice' };
      case 'compare': return { title: 'Patent Comparison', desc: 'Side-by-side technical evaluation & combination gap analysis' };
      case 'innovation': return { title: 'Innovation Refinement', desc: 'Concept coverage, whitespace detection & differentiation paths' };
      case 'reports': return { title: 'Research Reports', desc: 'Publication-grade landscape synthesis with PDF & Markdown export' };
      case 'results': return { title: 'Intelligence Center', desc: 'Deep-dive analysis, novelty scores, and technology clusters' };
      case 'knowledge': return { title: 'Knowledge Ingestion', desc: 'Indian patent corpus indexation & live EPO connection' };
      case 'docs': return { title: 'Documentation', desc: 'Architecture, API endpoints, and retrieval schemas' };
      case 'settings': return { title: 'Settings', desc: 'System configuration, API keys, and environment toggles' };
      default: return { title: 'PatentIQ', desc: 'Enterprise Patent Intelligence' };
    }
  };

  const currentViewMeta = getPageTitle(activeTab);

  return (
    <div className="app-container">
      {/* PERSISTENT LEFT SIDEBAR: Visible on analytical workspaces, hidden on Home Landing */}
      {activeTab !== 'home' && (
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`} aria-label="Sidebar Navigation">
        <div>
          {/* Sidebar Header & Brand */}
          <div className="sidebar-header">
            <div className="sidebar-brand">
              <div className="sidebar-logo-icon">IQ</div>
              {!sidebarCollapsed && <span className="sidebar-logo-text">PatentIQ</span>}
            </div>
            <button 
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="sidebar-collapse-btn"
              title={sidebarCollapsed ? 'Expand Navigation' : 'Collapse Navigation'}
              aria-label={sidebarCollapsed ? 'Expand Navigation' : 'Collapse Navigation'}
            >
              <Icon name={sidebarCollapsed ? 'chevron-right' : 'chevron-left'} size={14} />
            </button>
          </div>

          {/* Primary Navigation Section */}
          <nav className="sidebar-menu">
            {!sidebarCollapsed && <span className="sidebar-section-label">Research Intelligence</span>}
            {primaryNavItems.map((item) => (
              <button 
                key={item.id}
                className={`sidebar-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
                title={sidebarCollapsed ? item.label : ''}
              >
                <span className="sidebar-item-icon">
                  <Icon name={item.icon} size={16} />
                </span>
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            ))}

            {!sidebarCollapsed && <span className="sidebar-section-label" style={{ marginTop: '10px' }}>Platform</span>}
            {secondaryNavItems.map((item) => (
              <button 
                key={item.id}
                className={`sidebar-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
                title={sidebarCollapsed ? item.label : ''}
              >
                <span className="sidebar-item-icon">
                  <Icon name={item.icon} size={16} />
                </span>
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </nav>
        </div>

        {/* Sidebar Footer Status Indicator */}
        <div className="sidebar-footer">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11.5px', color: 'var(--text-secondary)', justifyContent: sidebarCollapsed ? 'center' : 'flex-start' }}>
            <span className={`status-indicator ${badge.statusClass}`} title={badge.text}></span>
            {!sidebarCollapsed && (
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{badge.text}</span>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>115k Patents + EPO Live</span>
              </div>
            )}
          </div>
        </div>
      </aside>
      )}

      {/* MAIN CONTENT VIEWPORT */}
      <div className="main-viewport">
        {/* TOP BAR: Displayed on analytical workspaces & tools */}
        {activeTab !== 'home' && (
          <header className="top-bar">
            <div className="top-bar-left">
              <div>
                <h1 className="top-bar-title">{currentViewMeta.title}</h1>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>{currentViewMeta.desc}</p>
              </div>
            </div>
            <div className="top-bar-right">
              <button 
                onClick={() => setActiveTab('home')}
                className="btn-secondary"
                style={{ padding: '5px 12px', fontSize: '12px' }}
                title="Return to Landing Overview"
              >
                <Icon name="home" size={13} />
                <span>Overview</span>
              </button>

              <span className="top-bar-badge">Enterprise Edition</span>

              {/* Theme Toggle Button */}
              <button 
                onClick={toggleTheme}
                className="theme-toggle-btn"
                title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                aria-label={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                <Icon name={theme === 'dark' ? 'sun' : 'moon'} size={14} color="var(--primary)" />
                <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
              </button>

              {patentData?.patents?.length > 0 && (
                <button 
                  onClick={() => setActiveTab('results')}
                  className="btn-secondary"
                  style={{ padding: '4px 10px', fontSize: '12px' }}
                >
                  Active Search ({patentData.patents.length})
                </button>
              )}
            </div>
          </header>
        )}

        {/* Global Error Banner */}
        {errorMsg && (
          <div className="container" style={{ paddingBottom: 0 }}>
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
              <span><strong>Execution Error:</strong> {errorMsg}</span>
              <button 
                onClick={() => setErrorMsg(null)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  fontSize: '18px',
                  lineHeight: 1
                }}
                aria-label="Dismiss Error"
              >
                x
              </button>
            </div>
          </div>
        )}

        {/* Routed views */}
        {activeTab === 'home' && (
          <Home onNavigate={handleNavigate} theme={theme} onToggleTheme={toggleTheme} />
        )}
        {activeTab === 'workspace' && (
          <Workspace 
            onAnalyze={handleAnalyze} 
            isAnalyzing={isAnalyzing} 
            history={historyQueries}
            onSelectHistoryItem={handleSelectHistoryItem}
          />
        )}
        {activeTab === 'copilot' && (
          <Copilot />
        )}
        {activeTab === 'compare' && (
          <PatentComparison 
            initialPatents={comparisonPatents}
            availablePatents={patentData?.patents || []}
            onNavigate={setActiveTab}
          />
        )}
        {activeTab === 'innovation' && (
          <InnovationRefinement 
            onNavigate={setActiveTab}
            initialIdea={patentData?.ideaText || ''}
          />
        )}
        {activeTab === 'reports' && (
          <ReportWorkspace 
            onNavigate={setActiveTab}
            initialTopic={patentData?.ideaText || ''}
            initialPatents={patentData?.patents || []}
          />
        )}
        {activeTab === 'results' && (
          <Results 
            data={patentData} 
            onNavigate={setActiveTab} 
            onStartComparison={handleStartComparison}
            onDeepDive={(patent) => {
              setComparisonPatents([patent]);
              setActiveTab('compare');
            }}
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
