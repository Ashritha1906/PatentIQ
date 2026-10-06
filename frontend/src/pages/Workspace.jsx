import React, { useState, useEffect } from 'react';

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

export default function Workspace({ onAnalyze, isAnalyzing, history, onSelectHistoryItem }) {
  const [title, setTitle] = useState('');
  const [ideaText, setIdeaText] = useState('');
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
    
    // Create default title if missing
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

  // Word & Character counts
  const wordCount = ideaText.trim() ? ideaText.trim().split(/\s+/).length : 0;
  const charCount = ideaText.length;
  const progressPercentage = ((loadingStep + 1) / STEPS.length) * 100;

  return (
    <div className="container" style={{ margin: '30px auto' }}>
      <div style={{ marginBottom: '18px' }}>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
          Interactive Workspace
        </span>
        <h1 style={{ fontSize: '26px', fontWeight: 700, color: '#fff' }}>Research Workspace</h1>
      </div>

      <div className="workspace-grid">
        {/* COLUMN 1: Filters & History */}
        <div className="workspace-column workspace-history-col">
          {/* Advanced Filters */}
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '12px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
              Retrieval Filters
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="input-label" htmlFor="topKSelect" style={{ fontSize: '10px' }}>Top K Matches</label>
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
                <label className="input-label" htmlFor="domainInput" style={{ fontSize: '10px' }}>Domain Class</label>
                <input
                  id="domainInput"
                  type="text"
                  className="text-field"
                  placeholder="e.g. AI, Healthcare"
                  value={domainFilter}
                  onChange={(e) => setDomainFilter(e.target.value)}
                />
              </div>

              <div>
                <label className="input-label" htmlFor="applicantInput" style={{ fontSize: '10px' }}>Applicant Name</label>
                <input
                  id="applicantInput"
                  type="text"
                  className="text-field"
                  placeholder="e.g. Samsung, Huawei"
                  value={applicantFilter}
                  onChange={(e) => setApplicantFilter(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* History of Previous Runs */}
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', flex: 1 }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '12px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
              Queries History
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '350px', overflowY: 'auto' }}>
              {history && history.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => onSelectHistoryItem(item)}
                  style={{
                    padding: '10px',
                    borderRadius: 'var(--border-radius-sm)',
                    background: 'var(--bg-surface-secondary)',
                    border: '1px solid var(--border-neutral)',
                    cursor: 'pointer',
                    transition: 'var(--transition-fast)'
                  }}
                  className="interactive-card"
                >
                  <div style={{ fontSize: '12.5px', fontWeight: 600, color: '#fff', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {item.title}
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    Score: <strong>{(item.data?.novelty_score?.score ?? item.data?.novelty_score?.novelty_score ?? item.data?.novelty_score?.overall_novelty_score ?? 0)}%</strong>
                  </div>
                </div>
              ))}
              {(!history || history.length === 0) && (
                <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
                  No previous runs
                </div>
              )}
            </div>
          </div>
        </div>

        {/* COLUMN 2: Idea Editor (Center) */}
        <div className="workspace-column" style={{ flex: 1 }}>
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '16px' }}>
                <label className="input-label" htmlFor="titleInput">Invention Title</label>
                <input
                  id="titleInput"
                  type="text"
                  className="text-field"
                  placeholder="e.g. Edge LLM Video Compression"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={isAnalyzing}
                />
              </div>

              <div style={{ marginBottom: '8px' }}>
                <label className="input-label" htmlFor="ideaText">Technical Description</label>
                <textarea
                  id="ideaText"
                  className="textarea-field"
                  placeholder="Describe the technology or invention you want to research in natural language (e.g. Find patents related to AI-based detection of diabetic retinopathy using retinal images)..."
                  value={ideaText}
                  onChange={(e) => setIdeaText(e.target.value)}
                  disabled={isAnalyzing}
                  style={{ height: '220px' }}
                />
              </div>

              {/* Word & Char counter indicators */}
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '20px' }}>
                <span>Words: <strong>{wordCount}</strong></span>
                <span>Characters: <strong>{charCount} / 2000</strong></span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={isAnalyzing || !ideaText.trim()}
                  style={{ padding: '12px 24px', fontSize: '13.5px', fontWeight: 600 }}
                >
                  {isAnalyzing ? 'Processing...' : 'Run Prior Art Analysis'}
                </button>
              </div>
            </form>
          </div>

          {/* Quick-Start suggestions */}
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '12px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
              Quick Templates
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
              {SUGGESTIONS.map((s, idx) => (
                <div
                  key={idx}
                  className="panel interactive template-card"
                  onClick={() => !isAnalyzing && handleSelectSuggestion(s)}
                  style={{
                    background: 'var(--bg-surface-secondary)',
                    padding: '12px',
                    cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                    opacity: isAnalyzing ? 0.5 : 1
                  }}
                >
                  <div className="template-category" style={{ fontSize: '9px' }}>{s.category}</div>
                  <div className="template-title" style={{ fontSize: '12px' }}>{s.title}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* COLUMN 3: AI Analysis Panel (Right) */}
        <div className="workspace-column workspace-status-col">
          {isAnalyzing ? (
            /* Active Loading checklist */
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', borderColor: 'var(--primary)' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '10px', textAlign: 'center' }}>
                RAG Pipeline Running
              </h3>
              
              <div className="progress-track" style={{ marginBottom: '20px' }}>
                <div 
                  className="progress-bar" 
                  style={{ 
                    width: `${progressPercentage}%`,
                    transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
                  }}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {STEPS.map((step, idx) => {
                  let statusClass = '';
                  let indicatorText = idx + 1;
                  
                  if (idx < loadingStep) {
                    statusClass = 'completed';
                    indicatorText = '✓';
                  } else if (idx === loadingStep) {
                    statusClass = 'active';
                  }

                  return (
                    <div key={idx} className={`step-item ${statusClass}`} style={{ fontSize: '13px' }}>
                      <div className="step-icon" style={{ width: '16px', height: '16px', fontSize: '9px' }}>
                        {indicatorText}
                      </div>
                      <span style={{ fontWeight: idx === loadingStep ? '600' : '400' }}>
                        {step}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Idle Guidelines Placeholder */
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', flex: 1 }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '12px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
                Guidelines & Tips
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                <div>
                  <strong style={{ color: '#fff', display: 'block', marginBottom: '4px' }}>💡 Detailed Queries Work Best</strong>
                  Describe the unique problem, implementation methods, and technical interfaces. The semantic engine compares concepts, not just keywords.
                </div>
                
                <div>
                  <strong style={{ color: '#fff', display: 'block', marginBottom: '4px' }}>⚙️ Utilize Filters</strong>
                  Constraint searches by primary technology classes (e.g. AI, Healthcare) or applicant fields to refine candidate alignments.
                </div>

                <div>
                  <strong style={{ color: '#fff', display: 'block', marginBottom: '4px' }}>📁 History Backups</strong>
                  Every successful run is cached in local memory. Select previous entries on the left panel to compare assessments instantly.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
