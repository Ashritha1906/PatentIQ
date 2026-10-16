import React, { useState } from 'react';
import { Icon } from '../components/Icons';
import HeroVisualization from '../components/HeroVisualization';
import Logo from '../components/Logo';

export function Home({ onNavigate, theme, onToggleTheme }) {
  const [consoleTab, setConsoleTab] = useState('retrieval');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollToSection = (id) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* 1. REFINED COMPACT NAVIGATION BAR */}
      <nav className="landing-navbar" aria-label="Main Navigation">
        <div className="landing-nav-inner">
          <Logo 
            size={34} 
            tagline="Enterprise AI" 
            onClick={() => scrollToSection('hero')} 
          />

          <div className="landing-nav-links">
            <button onClick={() => scrollToSection('platform')} className="landing-nav-link">Platform</button>
            <button onClick={() => scrollToSection('console')} className="landing-nav-link">Console</button>
            <button onClick={() => scrollToSection('capabilities')} className="landing-nav-link">Capabilities</button>
            <button onClick={() => scrollToSection('workflow')} className="landing-nav-link">Workflow</button>
            <button onClick={() => scrollToSection('integrity')} className="landing-nav-link">Integrity</button>
            <button onClick={() => onNavigate('copilot')} className="landing-nav-link" style={{ color: 'var(--primary)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
              <Icon name="copilot" size={13} color="var(--primary)" />
              <span>Copilot</span>
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button 
              onClick={onToggleTheme}
              className="theme-toggle-btn"
              title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              aria-label={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              <Icon name={theme === 'dark' ? 'sun' : 'moon'} size={14} color="var(--primary)" />
              <span>{theme === 'dark' ? 'Light' : 'Dark'}</span>
            </button>

            <button 
              onClick={() => onNavigate('workspace')}
              className="btn-shimmer-cta"
              style={{ padding: '8px 18px', fontSize: '13px' }}
            >
              <span>Open Workspace</span>
              <Icon name="arrow-right" size={14} />
            </button>

            <button 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="btn-secondary"
              style={{ display: 'none', padding: '6px 10px' }}
              id="mobile-menu-btn"
              aria-label="Toggle Navigation"
            >
              <Icon name={mobileMenuOpen ? 'close' : 'menu'} size={16} />
            </button>
          </div>
        </div>

        {/* Responsive Mobile Navigation Drawer */}
        <div className={`landing-mobile-menu ${mobileMenuOpen ? 'open' : ''}`}>
          <button onClick={() => scrollToSection('platform')} className="landing-nav-link" style={{ textAlign: 'left', padding: '8px 0' }}>Platform</button>
          <button onClick={() => scrollToSection('console')} className="landing-nav-link" style={{ textAlign: 'left', padding: '8px 0' }}>Interactive Console</button>
          <button onClick={() => scrollToSection('capabilities')} className="landing-nav-link" style={{ textAlign: 'left', padding: '8px 0' }}>Capabilities</button>
          <button onClick={() => scrollToSection('workflow')} className="landing-nav-link" style={{ textAlign: 'left', padding: '8px 0' }}>Workflow</button>
          <button onClick={() => scrollToSection('integrity')} className="landing-nav-link" style={{ textAlign: 'left', padding: '8px 0' }}>Integrity & Security</button>
          <button onClick={() => onNavigate('copilot')} className="landing-nav-link" style={{ textAlign: 'left', padding: '8px 0', color: 'var(--primary)' }}>Research Copilot</button>
          <button onClick={() => onNavigate('workspace')} className="btn-primary" style={{ marginTop: '8px' }}>Open Workspace</button>
        </div>
      </nav>

      {/* 2. SECTION 1: HERO & SIGNATURE PATENTIQ CONNECTED KNOWLEDGE VISUAL */}
      <section id="hero" className="hero-ambient-canvas">
        <div style={{ maxWidth: '1180px', margin: '0 auto', textAlign: 'center' }}>
          
          {/* Eyebrow Announcement Pill */}
          <div className="feature-pill-badge" style={{ marginBottom: '22px' }}>
            <span className="anim-pulse-dot" style={{ width: '7px', height: '7px', borderRadius: '50%', background: 'var(--success)', display: 'inline-block' }}></span>
            <span>Federated AI Patent Intelligence &bull; Live EPO EPS + Indian Patent Office</span>
          </div>

          {/* Master Typography Headline - Completely Unclipped */}
          <h1 className="hero-headline">
            Turn complex patent data into your <br />
            <span className="hero-gradient-text">next breakthrough.</span>
          </h1>

          {/* Concise Outcome-Focused Subheadline */}
          <p 
            style={{ 
              fontSize: '17px', 
              color: 'var(--text-secondary)', 
              lineHeight: 1.65, 
              maxWidth: '740px', 
              margin: '0 auto 32px auto' 
            }}
          >
            Discover relevant prior art, compare technical claims, explore innovation gaps, and build evidence-grounded research reports in one intelligent workspace.
          </p>

          {/* Primary & Secondary Action Buttons */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '14px', flexWrap: 'wrap', marginBottom: '20px' }}>
            <button 
              className="btn-shimmer-cta"
              onClick={() => onNavigate('workspace')}
              style={{ fontSize: '15px' }}
            >
              <span>Explore the Workspace</span>
              <Icon name="arrow-right" size={16} />
            </button>

            <button 
              className="btn-secondary"
              onClick={() => scrollToSection('workflow')}
              style={{ padding: '12px 24px', fontSize: '15px', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <span>See How It Works</span>
              <Icon name="chevron-down" size={14} color="var(--text-muted)" />
            </button>
          </div>

          {/* Concise Trust & Data-Source Indicator */}
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Federated intelligence bridging 115,000+ indexed Indian patent filings with live European Patent Office discovery.
          </div>

          {/* SIGNATURE PATENTIQ PRODUCT VISUAL CENTERPIECE */}
          <HeroVisualization onNavigate={onNavigate} />

        </div>
      </section>

      {/* 3. SECTION 2: CREDIBLE PRODUCT CONTEXT (DUAL-REGISTRY ARCHITECTURE) */}
      <section id="platform" style={{ padding: '80px 24px', background: 'var(--bg-surface-secondary)', borderBottom: '1px solid var(--border-neutral)' }}>
        <div style={{ maxWidth: '1180px', margin: '0 auto' }}>
          
          <div style={{ textAlign: 'center', marginBottom: '48px', maxWidth: '760px', margin: '0 auto 48px auto' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Dual-Registry Foundations
            </span>
            <h2 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.025em', marginTop: '6px', marginBottom: '12px' }}>
              Ground Truth Across Dual Patent Registries
            </h2>
            <p style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Federated multi-jurisdiction retrieval architecture eliminating blind spots between local dense vector corpora and live international publication gazettes.
            </p>
          </div>

          <div className="context-grid">
            {/* Card 1: Local Indian Patent Corpus */}
            <div className="context-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
                  <Icon name="database" size={20} />
                </div>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--success)', background: 'var(--success-glow)', padding: '3px 9px', borderRadius: '4px' }}>
                  Locally Indexed &bull; 115,000+ Records
                </span>
              </div>

              <h3 style={{ fontSize: '19px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
                Indian Patent Office (IPO) Corpus
              </h3>
              
              <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '20px' }}>
                Cleaned, validated, and vector-indexed publication records. Hybrid retrieval pairs 384-dimensional dense semantic embeddings with BM25 lexical ranking for maximum recall.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', background: 'var(--bg-surface-secondary)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-neutral)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Embedding Architecture:</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--primary)', fontWeight: 600 }}>all-MiniLM-L6-v2 (384-D)</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Vector Store:</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', fontWeight: 600 }}>ChromaDB Local Collection</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Query Latency:</span>
                  <span style={{ color: 'var(--success)', fontWeight: 600 }}>&lt;40ms Local Similarity</span>
                </div>
              </div>
            </div>

            {/* Card 2: European Patent Office (EPO) Integration */}
            <div className="context-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'var(--accent-violet-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-violet)' }}>
                  <Icon name="network" size={20} />
                </div>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', background: 'var(--primary-glow)', padding: '3px 9px', borderRadius: '4px' }}>
                  Live On-Demand &bull; EPS v1.2 Gateway
                </span>
              </div>

              <h3 style={{ fontSize: '19px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
                European Patent Office (EPO) Integration
              </h3>
              
              <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '20px' }}>
                Direct REST connection to the European Publication Server. Enables on-demand discovery of recent European patent filings, published claims, and bibliographic metadata.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', background: 'var(--bg-surface-secondary)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-neutral)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>API Protocol:</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-violet)', fontWeight: 600 }}>EPO EPS REST API v1.2</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Data Provenance:</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', fontWeight: 600 }}>Official European Gazette</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Operational Mode:</span>
                  <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Federated Non-Mutating Query</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* 4. SECTION 3: INTERACTIVE RESEARCH CONSOLE */}
      <section id="console" style={{ padding: '80px 24px', background: 'var(--bg-base)' }}>
        <div style={{ maxWidth: '1180px', margin: '0 auto' }}>

          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Live Workspace Demonstration
            </span>
            <h2 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.025em', marginTop: '6px', marginBottom: '10px' }}>
              Experience the Research Workspace
            </h2>
            <p style={{ fontSize: '15px', color: 'var(--text-secondary)', maxWidth: '680px', margin: '0 auto' }}>
              Inspect prior-art candidate citations, side-by-side claim alignment matrices, novelty dial coverage, and executive report synthesis.
            </p>
          </div>

          <div className="app-window-frame" style={{ maxWidth: '1040px', margin: '0 auto', textAlign: 'left' }}>
            
            {/* Window Chrome Header Bar */}
            <div className="window-chrome-bar">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#EF4444', display: 'inline-block' }}></span>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#F59E0B', display: 'inline-block' }}></span>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#10B981', display: 'inline-block' }}></span>
                <span style={{ marginLeft: '12px', fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  PatentIQ Intelligence Console &bull; Grounded Session
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge-provenance combined" style={{ fontSize: '11px', padding: '2px 8px' }}>
                  Dual Registry Active
                </span>
              </div>
            </div>

            {/* Active Query Display Header */}
            <div style={{ padding: '16px 20px', background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-neutral)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)', padding: '10px 16px', borderRadius: 'var(--border-radius-md)' }}>
                <Icon name="search" size={17} color="var(--primary)" />
                <span style={{ fontSize: '13.5px', color: 'var(--text-primary)', fontWeight: 500, flex: 1 }}>
                  Solid-state electrolyte interface stabilization with in-situ protective interphase layer
                </span>
                <span style={{ fontSize: '11px', background: 'var(--primary-glow)', color: 'var(--primary)', padding: '3px 8px', borderRadius: '4px', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                  384-D Hybrid Vector
                </span>
              </div>
            </div>

            {/* 4 Interactive Console Tabs */}
            <div style={{ display: 'flex', borderBottom: '1px solid var(--border-neutral)', background: 'var(--bg-surface-secondary)', overflowX: 'auto' }}>
              {[
                { id: 'retrieval', label: '1. Prior-Art Candidates (4)' },
                { id: 'matrix', label: '2. Claims Comparison Matrix' },
                { id: 'novelty', label: '3. Novelty & Concept Coverage' },
                { id: 'report', label: '4. Executive Report Preview' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setConsoleTab(tab.id)}
                  style={{
                    padding: '12px 18px',
                    background: consoleTab === tab.id ? 'var(--bg-surface)' : 'transparent',
                    border: 'none',
                    borderBottom: consoleTab === tab.id ? '2px solid var(--primary)' : 'none',
                    color: consoleTab === tab.id ? 'var(--text-primary)' : 'var(--text-muted)',
                    fontSize: '12.5px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    transition: 'all var(--transition-fast)'
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Console Body Viewport */}
            <div style={{ padding: '24px', background: 'var(--bg-surface)' }}>
              
              {/* Tab 1: Live Retrieved Patent Cards */}
              {consoleTab === 'retrieval' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ padding: '16px', borderRadius: 'var(--border-radius-md)', background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span className="font-mono" style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 700 }}>
                        EP3892014A1 &bull; European Patent Office (EPO Live)
                      </span>
                      <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--success)', background: 'var(--success-glow)', padding: '2px 8px', borderRadius: '4px' }}>
                        91% Semantic Proximity
                      </span>
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                      Solid composite electrolyte with in-situ formed protective interphase layer
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      Applicant: European Battery Innovation Labs &bull; Class: H01M 10/0562, C08L 71/02
                    </div>
                  </div>

                  <div style={{ padding: '16px', borderRadius: 'var(--border-radius-md)', background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span className="font-mono" style={{ fontSize: '12px', color: 'var(--accent-violet)', fontWeight: 700 }}>
                        IN202341088921A &bull; Indian Patent Registry
                      </span>
                      <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', background: 'var(--primary-glow)', padding: '2px 8px', borderRadius: '4px' }}>
                        84% Semantic Proximity
                      </span>
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                      Surface-modified cathode active materials for high-voltage solid battery cells
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      Applicant: National Institute of Clean Energy &bull; Class: H01M 4/13, H01M 10/052
                    </div>
                  </div>

                  <div style={{ padding: '16px', borderRadius: 'var(--border-radius-md)', background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span className="font-mono" style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 700 }}>
                        EP3451290B1 &bull; European Patent Office (EPO Live)
                      </span>
                      <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--warning)', background: 'var(--warning-glow)', padding: '2px 8px', borderRadius: '4px' }}>
                        78% Semantic Proximity
                      </span>
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                      Solid polymer electrolyte composition and lithium-ion secondary battery comprising same
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      Applicant: Advanced Energy Storage SE &bull; Class: H01M 10/0565, H01M 4/62
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Claims Matrix */}
              {consoleTab === 'matrix' && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px' }}>
                  <div style={{ padding: '16px', background: 'var(--bg-surface-secondary)', borderRadius: 'var(--border-radius-md)', border: '1px solid var(--border-neutral)' }}>
                    <span style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--success)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
                      &check; Overlapping Mechanisms
                    </span>
                    <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                      Both filings disclose polymer-ceramic hybrid matrices with lithium-salt ionic transport channels to mitigate dendrite propagation.
                    </p>
                  </div>
                  <div style={{ padding: '16px', background: 'var(--bg-surface-secondary)', borderRadius: 'var(--border-radius-md)', border: '1px solid var(--border-neutral)' }}>
                    <span style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--accent-violet)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
                      &bull; Technical Divergence
                    </span>
                    <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                      EP3892014A1 utilizes UV photopolymerization while IN202341088921A specifies chemical vapor interface deposition.
                    </p>
                  </div>
                  <div style={{ padding: '16px', background: 'var(--bg-surface-secondary)', borderRadius: 'var(--border-radius-md)', border: '1px solid var(--border-neutral)' }}>
                    <span style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--warning)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
                      &Delta; Combination Gap Signal
                    </span>
                    <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                      Neither filing discloses room-temperature curing coupled with high-nickel NMC811 cathode interfaces.
                    </p>
                  </div>
                </div>
              )}

              {/* Tab 3: Novelty & Concept Coverage */}
              {consoleTab === 'novelty' && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '24px', flexWrap: 'wrap', marginBottom: '20px' }}>
                    <div style={{ textAlign: 'center', minWidth: '130px', padding: '14px 18px', background: 'var(--bg-surface-secondary)', borderRadius: 'var(--border-radius-md)', border: '1px solid var(--border-neutral)' }}>
                      <div style={{ fontSize: '38px', fontWeight: 800, color: 'var(--success)', fontFamily: 'var(--font-heading)' }}>
                        78%
                      </div>
                      <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        Estimated Novelty
                      </div>
                    </div>
                    <div style={{ flex: 1, minWidth: '240px' }}>
                      <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                        Defensibility Differentiation Window
                      </div>
                      <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                        While composite polymer electrolytes are moderately crowded across European registries, coupling in-situ photopolymerization with low-temperature curing represents an uncrowded whitespace vector.
                      </p>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
                    <div style={{ background: 'var(--bg-surface-secondary)', padding: '10px 14px', borderRadius: '6px', borderLeft: '3px solid var(--error)' }}>
                      <span style={{ fontSize: '11px', color: 'var(--error)', fontWeight: 700, display: 'block' }}>Strongly Represented</span>
                      <span style={{ fontSize: '12px', color: 'var(--text-primary)' }}>Polymer-ceramic composite</span>
                    </div>
                    <div style={{ background: 'var(--bg-surface-secondary)', padding: '10px 14px', borderRadius: '6px', borderLeft: '3px solid var(--warning)' }}>
                      <span style={{ fontSize: '11px', color: 'var(--warning)', fontWeight: 700, display: 'block' }}>Moderately Represented</span>
                      <span style={{ fontSize: '12px', color: 'var(--text-primary)' }}>Dendrite suppression layer</span>
                    </div>
                    <div style={{ background: 'var(--bg-surface-secondary)', padding: '10px 14px', borderRadius: '6px', borderLeft: '3px solid var(--primary)' }}>
                      <span style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: 700, display: 'block' }}>Weakly Represented</span>
                      <span style={{ fontSize: '12px', color: 'var(--text-primary)' }}>In-situ UV curing</span>
                    </div>
                    <div style={{ background: 'var(--bg-surface-secondary)', padding: '10px 14px', borderRadius: '6px', borderLeft: '3px solid var(--success)' }}>
                      <span style={{ fontSize: '11px', color: 'var(--success)', fontWeight: 700, display: 'block' }}>Minimally Represented</span>
                      <span style={{ fontSize: '12px', color: 'var(--text-primary)' }}>Low-temperature interphase</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 4: Executive Report Preview */}
              {consoleTab === 'report' && (
                <div style={{ padding: '18px', background: 'var(--bg-surface-secondary)', borderRadius: 'var(--border-radius-md)', border: '1px solid var(--border-neutral)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <strong style={{ fontSize: '13.5px', color: 'var(--text-primary)' }}>PatentIQ Research Intelligence Report #2026-X</strong>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Audit Provenance Verified</span>
                  </div>
                  <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: '0 0 14px 0' }}>
                    Structured executive synthesis evaluating 4 primary prior-art citations, 2 shared claim mechanisms, and 1 uncrowded differentiation opportunity. Fully exportable in vector PDF and GitHub-flavored Markdown.
                  </p>
                  <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                    <button className="btn-secondary" onClick={() => onNavigate('reports')} style={{ padding: '6px 14px', fontSize: '12px' }}>
                      <Icon name="download" size={13} />
                      <span>Download PDF Report</span>
                    </button>
                    <button className="btn-secondary" onClick={() => onNavigate('reports')} style={{ padding: '6px 14px', fontSize: '12px' }}>
                      <Icon name="file-text" size={13} />
                      <span>Export Markdown</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Action Bar inside Console */}
              <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-neutral)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  Grounding: 115k+ Indian Records &bull; Live European Patent Office EPS
                </span>
                <button 
                  onClick={() => onNavigate('workspace')} 
                  className="btn-primary" 
                  style={{ padding: '6px 14px', fontSize: '12.5px', fontWeight: 600 }}
                >
                  <span>Launch Live Search In Workspace</span>
                  <Icon name="arrow-right" size={13} />
                </button>
              </div>

            </div>

          </div>

        </div>
      </section>

      {/* 5. SECTION 4: PRODUCT CAPABILITIES (DIVERSE LAYOUTS) */}
      <section id="capabilities" style={{ padding: '80px 24px', background: 'var(--bg-surface-secondary)', borderTop: '1px solid var(--border-neutral)', borderBottom: '1px solid var(--border-neutral)' }}>
        <div style={{ maxWidth: '1180px', margin: '0 auto' }}>
          
          <div style={{ textAlign: 'center', marginBottom: '48px', maxWidth: '740px', margin: '0 auto 48px auto' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Engineered Capabilities
            </span>
            <h2 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.025em', marginTop: '6px', marginBottom: '12px' }}>
              The Five Pillars of Patent Intelligence
            </h2>
            <p style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              A unified scientific intelligence suite eliminating manual spreadsheet comparisons, missed prior art, and ungrounded LLM hallucinations.
            </p>
          </div>

          <div className="bento-grid">
            
            {/* Capability 1 (Col 7): AI Research Copilot */}
            <div className="bento-card bento-col-7" onClick={() => onNavigate('copilot')} style={{ cursor: 'pointer' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
                    <Icon name="copilot" size={18} />
                  </div>
                  <div>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase' }}>Feature 01</span>
                    <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>AI Research Copilot</h3>
                  </div>
                </div>

                <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '20px' }}>
                  Conversational prior-art intelligence with multi-turn grounding, live claim citations, and browser Web Speech API voice synthesis.
                </p>

                {/* Simulated Audio Waveform Bar */}
                <div style={{ background: 'var(--bg-surface-secondary)', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-neutral)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <Icon name="mic" size={14} color="var(--primary)" />
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>Natural Speech & Text Interrogation</span>
                    <div style={{ display: 'flex', gap: '2px', marginLeft: 'auto', alignItems: 'center' }}>
                      <span style={{ width: '3px', height: '12px', background: 'var(--primary)', borderRadius: '2px' }}></span>
                      <span style={{ width: '3px', height: '18px', background: 'var(--accent-violet)', borderRadius: '2px' }}></span>
                      <span style={{ width: '3px', height: '8px', background: 'var(--primary)', borderRadius: '2px' }}></span>
                      <span style={{ width: '3px', height: '14px', background: 'var(--primary)', borderRadius: '2px' }}></span>
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Copilot Answer:</span> "Comparing claims across EP3892014A1 reveals edge thresholding filters reduce downlink latency by 64%."
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12.5px', fontWeight: 600, color: 'var(--primary)' }}>
                <span>Launch Research Copilot</span>
                <Icon name="arrow-right" size={14} />
              </div>
            </div>

            {/* Capability 2 (Col 5): Federated Retrieval */}
            <div className="bento-card bento-col-5" onClick={() => onNavigate('workspace')} style={{ cursor: 'pointer' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--accent-violet-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-violet)' }}>
                    <Icon name="network" size={18} />
                  </div>
                  <div>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-violet)', textTransform: 'uppercase' }}>Feature 02</span>
                    <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Federated Retrieval</h3>
                  </div>
                </div>

                <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '20px' }}>
                  Dual-registry architecture querying local Indian patent vector stores and live European Patent Office databases in parallel.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-surface-secondary)', padding: '8px 12px', borderRadius: '6px', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-primary)' }}>Indian Patent Corpus</span>
                    <span style={{ color: 'var(--success)', fontWeight: 600 }}>115,000+ Indexed</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-surface-secondary)', padding: '8px 12px', borderRadius: '6px', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-primary)' }}>EPO European Publication Server</span>
                    <span style={{ color: 'var(--success)', fontWeight: 600 }}>Live EPS v1.2</span>
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12.5px', fontWeight: 600, color: 'var(--primary)' }}>
                <span>Open Federated Search</span>
                <Icon name="arrow-right" size={14} />
              </div>
            </div>

            {/* Capability 3 (Col 5): Patent Comparison Matrix */}
            <div className="bento-card bento-col-5" onClick={() => onNavigate('compare')} style={{ cursor: 'pointer' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
                    <Icon name="compare" size={18} />
                  </div>
                  <div>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase' }}>Feature 03</span>
                    <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Comparison Matrix</h3>
                  </div>
                </div>

                <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '20px' }}>
                  Side-by-side claim matrix across 2 to 3 patents isolating overlapping mechanisms, technical divergence, and combination gap signals.
                </p>

                <div style={{ background: 'var(--bg-surface-secondary)', padding: '10px 12px', borderRadius: '6px', fontSize: '11.5px', color: 'var(--text-secondary)' }}>
                  <strong style={{ color: 'var(--warning)', display: 'block', marginBottom: '2px' }}>Gap Detection:</strong>
                  Identifies claims combinations unrepresented in prior filings.
                </div>
              </div>

              <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12.5px', fontWeight: 600, color: 'var(--primary)' }}>
                <span>Launch Comparison Matrix</span>
                <Icon name="arrow-right" size={14} />
              </div>
            </div>

            {/* Capability 4 (Col 7): Innovation Refinement */}
            <div className="bento-card bento-col-7" onClick={() => onNavigate('innovation')} style={{ cursor: 'pointer' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--accent-violet-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-violet)' }}>
                      <Icon name="innovation" size={18} />
                    </div>
                    <div>
                      <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-violet)', textTransform: 'uppercase' }}>Feature 04</span>
                      <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Innovation Refinement</h3>
                    </div>
                  </div>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--success)' }}>78% Novelty Dial</span>
                </div>

                <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '20px' }}>
                  Evaluate technical disclosures against prior art with 4-tier concept coverage (Strong, Moderate, Weak, Minimal), novelty gauge diagnostics, and differentiation vectors.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', textAlign: 'center' }}>
                  <div style={{ background: 'var(--bg-surface-secondary)', padding: '8px', borderRadius: '6px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--error)', fontWeight: 700, display: 'block' }}>Strong</span>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Crowded claims</span>
                  </div>
                  <div style={{ background: 'var(--bg-surface-secondary)', padding: '8px', borderRadius: '6px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--warning)', fontWeight: 700, display: 'block' }}>Moderate</span>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Analogous art</span>
                  </div>
                  <div style={{ background: 'var(--bg-surface-secondary)', padding: '8px', borderRadius: '6px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--success)', fontWeight: 700, display: 'block' }}>Minimal</span>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>True Whitespace</span>
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12.5px', fontWeight: 600, color: 'var(--accent-violet)' }}>
                <span>Run Innovation Diagnostic</span>
                <Icon name="arrow-right" size={14} />
              </div>
            </div>

            {/* Capability 5 (Col 12): Research Reports */}
            <div className="bento-card bento-col-12" onClick={() => onNavigate('reports')} style={{ cursor: 'pointer' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
                      <Icon name="reports" size={16} />
                    </div>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase' }}>Feature 05 &bull; Export Suite</span>
                  </div>
                  <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                    Publication-Grade Technical Intelligence Reports
                  </h3>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0, maxWidth: '640px' }}>
                    Export structured prior-art landscapes, competitor distributions, and novel claim audits with one-click PDF and Markdown export.
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn-secondary" style={{ padding: '6px 14px', fontSize: '12.5px' }}>
                    <Icon name="download" size={13} />
                    <span>Download PDF</span>
                  </button>
                  <button className="btn-secondary" style={{ padding: '6px 14px', fontSize: '12.5px' }}>
                    <Icon name="file-text" size={13} />
                    <span>Export Markdown</span>
                  </button>
                </div>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* 6. SECTION 5: HOW THE WORKFLOW CONNECTS */}
      <section id="workflow" style={{ padding: '80px 24px', background: 'var(--bg-base)' }}>
        <div style={{ maxWidth: '1180px', margin: '0 auto' }}>
          
          <div style={{ textAlign: 'center', marginBottom: '48px', maxWidth: '740px', margin: '0 auto 48px auto' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Connected Research Workflow
            </span>
            <h2 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.025em', marginTop: '6px', marginBottom: '12px' }}>
              How PatentIQ Connects the Discovery Journey
            </h2>
            <p style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              From initial technical abstract to verified executive intelligence brief in five seamless, evidence-grounded stages.
            </p>
          </div>

          <div className="workflow-pipeline">
            
            {/* Step 1 */}
            <div className="workflow-step-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--primary)', fontFamily: 'var(--font-mono)' }}>01</span>
                <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: 'var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
                  <Icon name="search" size={14} />
                </div>
              </div>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>Research Idea</h3>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                Input natural language disclosure, problem statements, or draft claim concepts without complex boolean syntax.
              </p>
            </div>

            {/* Step 2 */}
            <div className="workflow-step-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--accent-violet)', fontFamily: 'var(--font-mono)' }}>02</span>
                <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: 'var(--accent-violet-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-violet)' }}>
                  <Icon name="network" size={14} />
                </div>
              </div>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>Prior-Art Retrieval</h3>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                Parallel federated execution across 115,000+ local Indian records and live European Patent Office databases.
              </p>
            </div>

            {/* Step 3 */}
            <div className="workflow-step-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--warning)', fontFamily: 'var(--font-mono)' }}>03</span>
                <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: 'var(--warning-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--warning)' }}>
                  <Icon name="compare" size={14} />
                </div>
              </div>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>Claims Comparison</h3>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                Dissect technical overlap, identify mechanism divergence, and detect uncrowded combination gap signals.
              </p>
            </div>

            {/* Step 4 */}
            <div className="workflow-step-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--success)', fontFamily: 'var(--font-mono)' }}>04</span>
                <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: 'var(--success-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--success)' }}>
                  <Icon name="innovation" size={14} />
                </div>
              </div>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>Innovation Refinement</h3>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                Analyze 4-tier concept coverage, evaluate novelty dial diagnostics, and pinpoint defensibility vectors.
              </p>
            </div>

            {/* Step 5 */}
            <div className="workflow-step-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--primary)', fontFamily: 'var(--font-mono)' }}>05</span>
                <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: 'var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
                  <Icon name="file-text" size={14} />
                </div>
              </div>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>Research Report</h3>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                Synthesize audit-ready executive intelligence briefs with one-click vector PDF and GitHub-flavored Markdown export.
              </p>
            </div>

          </div>

        </div>
      </section>

      {/* 7. SECTION 6: RESEARCH INTEGRITY & LEGAL GUARDRAILS */}
      <section id="integrity" style={{ padding: '80px 24px', background: 'var(--bg-surface-secondary)', borderTop: '1px solid var(--border-neutral)', borderBottom: '1px solid var(--border-neutral)' }}>
        <div style={{ maxWidth: '1180px', margin: '0 auto' }}>
          
          <div style={{ textAlign: 'center', marginBottom: '48px', maxWidth: '740px', margin: '0 auto 48px auto' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--success)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Responsible AI & Research Integrity
            </span>
            <h2 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.025em', marginTop: '6px', marginBottom: '12px' }}>
              Built For Audit-Grade Legal & R&D Workflows
            </h2>
            <p style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Enterprise-ready controls ensuring evidence traceability, source provenance verification, and responsible AI guardrails.
            </p>
          </div>

          <div className="trust-grid">
            <div className="trust-card">
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)', marginBottom: '14px' }}>
                <Icon name="shield" size={18} />
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>Strict Source Grounding</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Every synthesized answer and claim citation is strictly mapped to authentic patent publication records. Zero unverified hallucinations.
              </p>
            </div>

            <div className="trust-card">
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--accent-violet-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-violet)', marginBottom: '14px' }}>
                <Icon name="network" size={18} />
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>Multi-Jurisdiction Breadth</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Unified coverage bridging Indian intellectual property datasets and live European Patent Office gazette feeds.
              </p>
            </div>

            <div className="trust-card">
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--success-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--success)', marginBottom: '14px' }}>
                <Icon name="check" size={18} />
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>Auditable Provenance</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Comprehensive publication metadata, applicant lineage, IPC/CPC classification trees, and reproducible retrieval parameters.
              </p>
            </div>

            <div className="trust-card">
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--warning-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--warning)', marginBottom: '14px' }}>
                <Icon name="info" size={18} />
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>Research Integrity</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Algorithmic prior art exploration assisting technical decision-makers. Transparent disclosure that outputs do not constitute legal patentability opinions.
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* 8. SECTION 7: FINAL CALL TO ACTION */}
      <section style={{ padding: '88px 24px', textAlign: 'center', background: 'radial-gradient(ellipse at 50% 100%, var(--primary-glow) 0%, var(--bg-surface) 80%)' }}>
        <div style={{ maxWidth: '740px', margin: '0 auto' }}>
          <h2 style={{ fontSize: 'clamp(28px, 4vw, 42px)', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em', lineHeight: 1.2, marginBottom: '16px' }}>
            Ready to turn complex prior art into defensible breakthroughs?
          </h2>
          <p style={{ fontSize: '16px', color: 'var(--text-secondary)', lineHeight: 1.65, marginBottom: '36px' }}>
            Explore prior art, understand technical relationships, and make your research more informed with federated AI intelligence.
          </p>
          <button 
            className="btn-shimmer-cta"
            onClick={() => onNavigate('workspace')}
            style={{ fontSize: '16px', padding: '14px 32px' }}
          >
            <span>Open Research Workspace</span>
            <Icon name="arrow-right" size={16} />
          </button>
        </div>
      </section>

      {/* 9. SECTION 8: BALANCED, COMPACT FOOTER */}
      <footer style={{ background: 'var(--bg-surface)', borderTop: '1px solid var(--border-neutral)', padding: '48px 24px 36px 24px', marginTop: 'auto' }}>
        <div style={{ maxWidth: '1180px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '32px', marginBottom: '36px' }}>
          <div>
            <div style={{ marginBottom: '14px' }}>
              <Logo size={28} />
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              Federated AI patent intelligence platform for deep-tech innovators, R&D engineering teams, and patent counsel.
            </p>
          </div>

          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase', marginBottom: '12px' }}>Navigation</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
              <button onClick={() => scrollToSection('hero')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Overview</button>
              <button onClick={() => scrollToSection('platform')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Dual-Registry Platform</button>
              <button onClick={() => scrollToSection('console')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Interactive Console</button>
              <button onClick={() => scrollToSection('capabilities')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Capabilities</button>
              <button onClick={() => scrollToSection('workflow')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Workflow</button>
              <button onClick={() => scrollToSection('integrity')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Integrity & Security</button>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase', marginBottom: '12px' }}>Research Modules</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
              <button onClick={() => onNavigate('workspace')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Patent Search</button>
              <button onClick={() => onNavigate('copilot')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>AI Research Copilot</button>
              <button onClick={() => onNavigate('compare')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Patent Comparison</button>
              <button onClick={() => onNavigate('innovation')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Innovation Refinement</button>
              <button onClick={() => onNavigate('reports')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', textAlign: 'left', cursor: 'pointer', padding: 0 }}>Research Reports</button>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase', marginBottom: '12px' }}>Research Integrity</div>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.55, margin: 0 }}>
              All similarity scores and novelty metrics represent automated algorithmic exploration grounded in authentic patent filings. PatentIQ does not provide legal patentability opinions or freedom-to-operate advice.
            </p>
          </div>
        </div>

        <div style={{ maxWidth: '1180px', margin: '0 auto', paddingTop: '20px', borderTop: '1px solid var(--border-neutral)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
          <span>&copy; {new Date().getFullYear()} PatentIQ Platform. Enterprise AI Patent Intelligence.</span>
          <span>Federated Multi-Jurisdiction Retrieval &bull; Verifiable Provenance</span>
        </div>
      </footer>

    </div>
  );
}

export default Home;
