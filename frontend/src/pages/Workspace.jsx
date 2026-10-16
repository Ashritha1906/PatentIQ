import React, { useState, useEffect } from 'react';
import { Icon } from '../components/Icons';

const SUGGESTIONS = [
  {
    category: "Generative AI",
    title: "Privacy-Preserving Edge LLM Fine-Tuning",
    text: "A system for fine-tuning large language models using federated learning on edge devices while preserving user privacy."
  },
  {
    category: "Smart Grid & IoT",
    title: "Decentralized Smart Battery Scheduling",
    text: "Decentralized scheduling algorithm for smart grid power optimization across multi-tenant home batteries."
  },
  {
    category: "Bio-Medical / Wearables",
    title: "Wearable Anomaly Detection Biosensor",
    text: "A wearable biosensor device that continuously monitors glucose and blood oxygen levels, using local anomaly detection algorithms to warn of sudden spikes."
  },
  {
    category: "Cybersecurity",
    title: "Zero-Knowledge Authentication for Supply Chain",
    text: "Zero-knowledge proof authentication mechanism for distributed ledger supply chain verification."
  },
  {
    category: "Autonomous Systems",
    title: "Low-Visibility LiDAR Sensor Fusion Network",
    text: "Real-time LiDAR sensor fusion network using transformer architectures for collision avoidance in low-visibility environments."
  }
];

const STEPS = [
  "Understanding Technical Idea",
  "Searching Patent Vector Index",
  "Filtering Prior Art & Competitors",
  "Calculating Novelty Percentages",
  "Synthesizing Gemini RAG Report"
];

export default function Workspace({ onAnalyze, isAnalyzing, history, onSelectHistoryItem, initialQuery = "" }) {
  const [title, setTitle] = useState('');
  const [ideaText, setIdeaText] = useState(initialQuery || '');

  useEffect(() => {
    if (initialQuery) {
      setIdeaText(initialQuery);
      setTitle(initialQuery.substring(0, 40) + '...');
    }
  }, [initialQuery]);
  const [topK, setTopK] = useState(5);
  const [domainFilter, setDomainFilter] = useState('');
  const [applicantFilter, setApplicantFilter] = useState('');
  const [loadingStep, setLoadingStep] = useState(0);

  // Sequentially animate checklist steps when analysis is active
  useEffect(() => {
    if (!isAnalyzing) {
      setLoadingStep(0);
      return;
    }

    const interval = setInterval(() => {
      setLoadingStep((prev) => {
        if (prev < STEPS.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 900);

    return () => clearInterval(interval);
  }, [isAnalyzing]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!ideaText.trim()) return;
    
    const finalTitle = title.trim() || ideaText.trim().substring(0, 35) + '...';
    onAnalyze({
      title: finalTitle,
      ideaText,
      topK: Number(topK),
      domainFilter,
      applicantFilter
    });
  };

  const handleSelectSuggestion = (s) => {
    setTitle(s.title);
    setIdeaText(s.text);
  };

  const wordCount = ideaText.trim() ? ideaText.trim().split(/\s+/).length : 0;
  const charCount = ideaText.length;
  const progressPercentage = ((loadingStep + 1) / STEPS.length) * 100;

  return (
    <div className="container" style={{ margin: '16px auto' }}>
      <div style={{ marginBottom: '16px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#fff', marginBottom: '4px' }}>
          Prior-Art Search Workspace
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
          Input invention specifications in natural language to perform federated vector retrieval across Indian and EPO patents.
        </p>
      </div>

      <div className="workspace-grid">
        {/* COLUMN 1: Filters & History */}
        <div className="workspace-column workspace-history-col">
          {/* Advanced Filters */}
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
              <Icon name="filter" size={14} color="var(--primary)" />
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#fff', margin: 0 }}>
                Retrieval Parameters
              </h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label className="input-label" htmlFor="topKSelect" style={{ fontSize: '10px' }}>Top Candidates</label>
                <select
                  id="topKSelect"
                  className="select-field"
                  value={topK}
                  onChange={(e) => setTopK(e.target.value)}
                >
                  <option value={3}>Top 3 Patents</option>
                  <option value={5}>Top 5 Patents</option>
                  <option value={10}>Top 10 Patents</option>
                </select>
              </div>

              <div>
                <label className="input-label" htmlFor="domainInput" style={{ fontSize: '10px' }}>Technology Domain</label>
                <input
                  id="domainInput"
                  type="text"
                  className="text-field"
                  placeholder="e.g. AI, Biomarkers"
                  value={domainFilter}
                  onChange={(e) => setDomainFilter(e.target.value)}
                />
              </div>

              <div>
                <label className="input-label" htmlFor="applicantInput" style={{ fontSize: '10px' }}>Target Applicant</label>
                <input
                  id="applicantInput"
                  type="text"
                  className="text-field"
                  placeholder="e.g. Siemens, Philips"
                  value={applicantFilter}
                  onChange={(e) => setApplicantFilter(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* History of Previous Runs */}
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', flex: 1 }}>
            <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#fff', marginBottom: '12px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
              Search History
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '350px', overflowY: 'auto' }}>
              {history && history.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => onSelectHistoryItem(item)}
                  style={{
                    padding: '8px 10px',
                    borderRadius: 'var(--border-radius-sm)',
                    background: 'var(--bg-surface-secondary)',
                    border: '1px solid var(--border-neutral)',
                    cursor: 'pointer',
                    transition: 'var(--transition-fast)'
                  }}
                  className="panel interactive"
                >
                  <div style={{ fontSize: '12px', fontWeight: 600, color: '#fff', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {item.title}
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    Novelty: <strong>{(item.data?.novelty_score?.score ?? item.data?.novelty_score?.novelty_score ?? item.data?.novelty_score?.overall_novelty_score ?? 0)}%</strong>
                  </div>
                </div>
              ))}
              {(!history || history.length === 0) && (
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
                  No previous searches
                </div>
              )}
            </div>
          </div>
        </div>

        {/* COLUMN 2: Idea Editor (Center) */}
        <div className="workspace-column" style={{ flex: 1 }}>
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '14px' }}>
                <label className="input-label" htmlFor="titleInput">Invention / Research Title</label>
                <input
                  id="titleInput"
                  type="text"
                  className="text-field"
                  placeholder="e.g. Edge LLM Video Compression Algorithm"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={isAnalyzing}
                />
              </div>

              <div style={{ marginBottom: '8px' }}>
                <label className="input-label" htmlFor="ideaText">Technical Invention Description</label>
                <textarea
                  id="ideaText"
                  className="textarea-field"
                  placeholder="Describe your technical invention, method, or system architecture in natural language. For example: A decentralized swarm navigation system for aerial drones using ultra-wideband relative localization, edge optical flow, and mesh consensus collision avoidance..."
                  value={ideaText}
                  onChange={(e) => setIdeaText(e.target.value)}
                  disabled={isAnalyzing}
                  style={{ height: '200px' }}
                />
              </div>

              {/* Word & Char counter indicators */}
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                <span>Words: <strong style={{ color: 'var(--text-secondary)' }}>{wordCount}</strong></span>
                <span>Characters: <strong style={{ color: 'var(--text-secondary)' }}>{charCount} / 2500</strong></span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={isAnalyzing || !ideaText.trim()}
                  style={{ padding: '10px 20px', fontSize: '13px' }}
                >
                  <Icon name="search" size={15} color="#080B12" />
                  {isAnalyzing ? 'Retrieving Prior Art...' : 'Search & Analyze Prior Art'}
                </button>
              </div>
            </form>
          </div>

          {/* Quick-Start suggestions */}
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#fff', marginBottom: '10px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
              Example Research Templates
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px' }}>
              {SUGGESTIONS.map((s, idx) => (
                <div
                  key={idx}
                  className="panel interactive"
                  onClick={() => !isAnalyzing && handleSelectSuggestion(s)}
                  style={{
                    background: 'var(--bg-surface-secondary)',
                    padding: '10px 12px',
                    cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                    opacity: isAnalyzing ? 0.5 : 1
                  }}
                >
                  <div style={{ fontSize: '9px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', marginBottom: '2px' }}>
                    {s.category}
                  </div>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.3 }}>
                    {s.title}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* COLUMN 3: AI Analysis Panel (Right) */}
        <div className="workspace-column workspace-status-col">
          {isAnalyzing ? (
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', borderColor: 'var(--primary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '12px' }}>
                <Icon name="sparkles" size={16} color="var(--primary)" />
                <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', margin: 0 }}>
                  Pipeline Executing
                </h3>
              </div>
              
              <div style={{ width: '100%', height: '4px', background: 'var(--bg-surface-secondary)', borderRadius: '2px', overflow: 'hidden', marginBottom: '18px' }}>
                <div 
                  style={{ 
                    width: `${progressPercentage}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, var(--primary), var(--accent-violet))',
                    transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
                  }}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {STEPS.map((step, idx) => {
                  const isPast = idx < loadingStep;
                  const isCurrent = idx === loadingStep;

                  return (
                    <div 
                      key={idx} 
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '8px', 
                        fontSize: '12px',
                        color: isPast ? 'var(--text-primary)' : isCurrent ? 'var(--primary)' : 'var(--text-muted)'
                      }}
                    >
                      <div 
                        style={{ 
                          width: '18px', 
                          height: '18px', 
                          borderRadius: '50%', 
                          background: isPast ? 'var(--success)' : isCurrent ? 'var(--primary-glow)' : 'var(--bg-surface-secondary)',
                          border: `1px solid ${isPast ? 'var(--success)' : isCurrent ? 'var(--primary)' : 'var(--border-neutral)'}`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '10px',
                          color: isPast ? '#fff' : isCurrent ? 'var(--primary)' : 'var(--text-muted)',
                          flexShrink: 0
                        }}
                      >
                        {isPast ? <Icon name="check" size={11} color="#fff" /> : idx + 1}
                      </div>
                      <span style={{ fontWeight: isCurrent ? 600 : 400 }}>
                        {step}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', flex: 1 }}>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#fff', marginBottom: '12px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
                Research Guidelines
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.55' }}>
                <div>
                  <strong style={{ color: '#fff', display: 'block', marginBottom: '2px' }}>Detailed Descriptions</strong>
                  Outline the underlying technical mechanism, structural elements, and data flow. The dense semantic embedder matches conceptual representations.
                </div>
                
                <div>
                  <strong style={{ color: '#fff', display: 'block', marginBottom: '2px' }}>Federated Scope</strong>
                  Queries automatically search the indexed Indian patent dataset (~115k records) and federate against live European Publication Server (EPO) records.
                </div>

                <div>
                  <strong style={{ color: '#fff', display: 'block', marginBottom: '2px' }}>Downstream Tools</strong>
                  Retrieved patents can be directly sent to Patent Comparison (Feature 2) or synthesized into Research Intelligence Reports (Feature 4).
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
