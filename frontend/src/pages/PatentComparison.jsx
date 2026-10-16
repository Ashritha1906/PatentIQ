import React, { useState, useEffect } from 'react';
import { comparePatents, getPatentDeepDive } from '../services/api';
import { Icon } from '../components/Icons';

/**
 * PatentComparison Component
 * Dedicated workspace for structured 2-3 patent technical comparisons and individual deep-dives.
 */
export default function PatentComparison({ 
  initialPatents = [], 
  availablePatents = [], 
  _onNavigate = null 
}) {
  const [selectedPatents, setSelectedPatents] = useState(initialPatents || []);
  const [comparisonData, setComparisonData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState(null);
  
  // Deep-Dive Modal State
  const [deepDivePatent, setDeepDivePatent] = useState(null);
  const [deepDiveData, setDeepDiveData] = useState(null);
  const [isDeepDiveLoading, setIsDeepDiveLoading] = useState(false);
  const [deepDiveError, setDeepDiveError] = useState(null);

  // Manual ID input state
  const [manualIdInput, setManualIdInput] = useState('');

  useEffect(() => {
    if (initialPatents && initialPatents.length >= 2 && initialPatents.length <= 3) {
      setSelectedPatents(initialPatents);
    }
  }, [initialPatents]);

  useEffect(() => {
    if (selectedPatents.length >= 2 && selectedPatents.length <= 3) {
      runComparison(selectedPatents);
    } else {
      setComparisonData(null);
    }
  }, [selectedPatents]);

  const runComparison = async (patentsToCompare) => {
    setIsLoading(true);
    setError(null);
    setLoadingStep(1);

    const stepInterval = setInterval(() => {
      setLoadingStep(prev => (prev < 4 ? prev + 1 : prev));
    }, 600);

    try {
      const response = await comparePatents({ patents: patentsToCompare });
      clearInterval(stepInterval);
      setComparisonData(response);
      setIsLoading(false);
    } catch (err) {
      clearInterval(stepInterval);
      console.error('Comparison error:', err);
      setError(err.message || 'Comparison processing failed. Please try again.');
      setIsLoading(false);
    }
  };

  const handleTogglePatent = (patent) => {
    const pid = patent.publication_number || patent.application_number;
    const isSelected = selectedPatents.some(p => (p.publication_number || p.application_number) === pid);

    if (isSelected) {
      setSelectedPatents(prev => prev.filter(p => (p.publication_number || p.application_number) !== pid));
    } else {
      if (selectedPatents.length >= 3) {
        setError('Comparison is limited to 3 patents. Remove one to add another.');
        return;
      }
      setError(null);
      setSelectedPatents(prev => [...prev, patent]);
    }
  };

  const handleAddManualId = () => {
    const trimmed = manualIdInput.trim();
    if (!trimmed) return;
    if (selectedPatents.length >= 3) {
      setError('Comparison is limited to 3 patents.');
      return;
    }
    const alreadySelected = selectedPatents.some(p => (p.publication_number || p.application_number) === trimmed);
    if (alreadySelected) {
      setError('This patent is already selected.');
      return;
    }
    const placeholder = {
      publication_number: trimmed,
      title: `Patent Document ${trimmed}`,
      abstract: 'Not available in retrieved evidence.',
      applicant: 'Not available in retrieved evidence.',
      provenance: { source: 'LOCAL', identifier: trimmed, confidence: 'PARTIAL' },
      partial_data: true
    };
    setSelectedPatents(prev => [...prev, placeholder]);
    setManualIdInput('');
    setError(null);
  };

  const handleOpenDeepDive = async (patent) => {
    setDeepDivePatent(patent);
    setDeepDiveData(null);
    setIsDeepDiveLoading(true);
    setDeepDiveError(null);

    try {
      const resp = await getPatentDeepDive({
        patent,
        comparisonContext: selectedPatents
      });
      setDeepDiveData(resp);
      setIsDeepDiveLoading(false);
    } catch (err) {
      console.error('Deep dive error:', err);
      setDeepDiveError(err.message || 'Failed to retrieve deep dive analysis.');
      setIsDeepDiveLoading(false);
    }
  };

  const getPatentIdentifier = (p) => p.publication_number || p.application_number || 'UNKNOWN';

  return (
    <div className="container" style={{ paddingBottom: '60px' }}>
      {/* HEADER */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <div style={{ width: "32px", height: "32px", borderRadius: "6px", background: "var(--primary-glow)", display: "flex", alignItems: "center", justifyContent: "center" }}><Icon name="compare" size={18} color="var(--primary)" /></div>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
              Patent Comparison & Deep-Dive Workspace
            </h1>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
              Compare technical approaches, shared concepts, and differences across selected patents.
            </p>
          </div>
        </div>

        {/* Legal Guardrail Notice */}
        <div 
          style={{ 
            background: 'rgba(59, 130, 246, 0.08)', 
            border: '1px solid rgba(59, 130, 246, 0.25)', 
            borderRadius: 'var(--border-radius-sm)',
            padding: '8px 14px',
            fontSize: '11px',
            color: '#93c5fd',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <Icon name="shield" size={14} color="var(--primary)" />
          <span>
            <strong>Research Intelligence Notice:</strong> This comparison provides automated technical analysis for research exploration. It does NOT constitute a legal determination of infringement, patentability, validity, or freedom to operate.
          </span>
        </div>
      </div>

      {/* SELECTION ROW */}
      <div className="panel panel-padding" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
              Selected Comparison Set ({selectedPatents.length}/3)
            </h3>
            <span style={{ fontSize: '12px', color: selectedPatents.length < 2 ? 'var(--warning)' : 'var(--text-muted)' }}>
              {selectedPatents.length === 0 && 'Select at least 2 patents to compare.'}
              {selectedPatents.length === 1 && '1 patent selected. Select at least 2 patents to compare.'}
              {selectedPatents.length === 2 && '2 patents selected for side-by-side analysis.'}
              {selectedPatents.length === 3 && '3 patents selected (maximum comparison limit reached).'}
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <input 
              type="text" 
              placeholder="Enter Patent ID (e.g. EP3456789)"
              value={manualIdInput}
              onChange={(e) => setManualIdInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddManualId()}
              style={{
                background: 'var(--bg-base)',
                border: '1px solid var(--border-neutral)',
                color: 'var(--text-primary)',
                fontSize: '12px',
                padding: '6px 10px',
                borderRadius: 'var(--border-radius-sm)',
                width: '190px'
              }}
            />
            <button 
              className="btn-secondary" 
              onClick={handleAddManualId}
              style={{ padding: '6px 12px', fontSize: '12px' }}
            >
              + Add ID
            </button>
            {selectedPatents.length > 0 && (
              <button 
                className="btn-secondary" 
                onClick={() => setSelectedPatents([])}
                style={{ padding: '6px 12px', fontSize: '12px', color: 'var(--text-muted)' }}
              >
                Clear All
              </button>
            )}
          </div>
        </div>

        {/* Selected Patent Cards Row */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: `repeat(${Math.max(selectedPatents.length, 1)}, minmax(280px, 1fr))`,
          gap: '16px' 
        }}>
          {selectedPatents.map((pat, idx) => {
            const pid = getPatentIdentifier(pat);
            const source = pat.source || (pat.provenance?.source) || 'LOCAL';
            return (
              <div 
                key={pid}
                style={{
                  background: 'var(--bg-surface-secondary)',
                  border: '1px solid var(--border-neutral)',
                  borderRadius: 'var(--border-radius-md)',
                  padding: '14px',
                  position: 'relative'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ 
                      fontSize: '11px', 
                      fontWeight: 700, 
                      color: 'var(--primary-light)', 
                      background: 'rgba(99, 102, 241, 0.15)',
                      padding: '2px 6px',
                      borderRadius: '4px'
                    }}>
                      Patent {String.fromCharCode(65 + idx)}
                    </span>
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {pid}
                    </span>
                    <span style={{ 
                      fontSize: '9px', 
                      fontWeight: 600,
                      color: source.includes('EPO') ? '#38bdf8' : 'var(--primary-light)', 
                      background: source.includes('EPO') ? 'rgba(56, 189, 248, 0.15)' : 'rgba(59, 130, 246, 0.1)', 
                      padding: '1px 6px', 
                      borderRadius: '4px'
                    }}>
                      {source}
                    </span>
                  </div>
                  <button 
                    onClick={() => handleTogglePatent(pat)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-muted)',
                      cursor: 'pointer',
                      fontSize: '14px',
                      lineHeight: 1
                    }}
                    title="Remove from comparison"
                  >
                    ✕
                  </button>
                </div>

                <h4 style={{ 
                  fontSize: '13px', 
                  fontWeight: 600, 
                  color: 'var(--text-primary)', 
                  margin: '4px 0 8px 0',
                  lineHeight: 1.4,
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}>
                  {pat.title}
                </h4>

                <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '12px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  <div><strong>Applicant:</strong> {pat.applicant || 'Not specified'}</div>
                  <div><strong>Publication Date:</strong> {pat.publication_date || 'N/A'}</div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <button 
                    className="btn-secondary"
                    onClick={() => handleOpenDeepDive(pat)}
                    style={{ 
                      padding: '4px 10px', 
                      fontSize: '11px',
                      color: 'var(--primary-light)',
                      borderColor: 'rgba(99, 102, 241, 0.4)',
                      background: 'rgba(99, 102, 241, 0.08)'
                    }}
                  >
                    Deep Dive
                  </button>
                  {pat.semantic_score && (
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      Sim: {Math.round(pat.semantic_score * 100)}%
                    </span>
                  )}
                </div>
              </div>
            );
          })}

          {selectedPatents.length === 0 && (
            <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)', gridColumn: '1 / -1' }}>
              No patents selected. Pick from recent results below or enter a patent identifier above.
            </div>
          )}
        </div>

        {/* Quick Pick From Available Search Results */}
        {availablePatents && availablePatents.length > 0 && selectedPatents.length < 3 && (
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-neutral)' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
              Quick-add from recent retrieval results:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {availablePatents.slice(0, 6).map((ap) => {
                const apId = getPatentIdentifier(ap);
                const isAlreadySelected = selectedPatents.some(p => getPatentIdentifier(p) === apId);
                if (isAlreadySelected) return null;
                return (
                  <button 
                    key={apId}
                    className="landscape-chip"
                    onClick={() => handleTogglePatent(ap)}
                    style={{
                      fontSize: '11px',
                      padding: '4px 8px',
                      background: 'var(--bg-surface-secondary)',
                      color: 'var(--text-primary)',
                      border: '1px solid var(--border-neutral)'
                    }}
                  >
                    + {apId}: {ap.title ? ap.title.slice(0, 30) + '...' : ''}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>      {/* ERROR BANNER */}
      {error && (
        <div style={{ 
          background: 'rgba(239, 68, 68, 0.1)', 
          border: '1px solid var(--error)', 
          color: 'var(--text-primary)',
          padding: '12px 16px',
          borderRadius: 'var(--border-radius-md)',
          fontSize: '13px',
          marginBottom: '24px'
        }}>
          <Icon name="info" size={14} color="var(--error)" /> {error}
        </div>
      )}

      {/* LOADING STATE */}
      {isLoading && (
        <div className="panel panel-padding" style={{ textAlign: 'center', padding: '48px 24px', marginBottom: '24px' }}>
          <div style={{ fontSize: '28px', marginBottom: '12px' }}></div>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
            Analyzing selected patents...
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
            {loadingStep === 1 && '1. Loading patent evidence & metadata...'}
            {loadingStep === 2 && '2. Extracting technical concepts & algorithms...'}
            {loadingStep === 3 && '3. Comparing architectures & computing overlap...'}
            {loadingStep >= 4 && '4. Synthesizing research comparison overview...'}
          </p>
          <div style={{ width: '200px', height: '4px', background: 'var(--bg-base)', borderRadius: '2px', margin: '0 auto', overflow: 'hidden' }}>
            <div style={{ width: `${loadingStep * 25}%`, height: '100%', background: 'var(--primary)', transition: 'width 0.4s ease' }} />
          </div>
        </div>
      )}

      {/* COMPARISON RESULTS */}
      {!isLoading && comparisonData && (
        <>
          {/* 1. AI COMPARISON SUMMARY */}
          <div className="panel panel-padding" style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h2 className="panel-title" style={{ margin: 0 }}>
                AI Comparison Summary
              </h2>
              <span style={{ fontSize: '11px', color: 'var(--primary-light)', background: 'rgba(99, 102, 241, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
                Evidence Grounded • Gemini Synthesized
              </span>
            </div>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.7', whiteSpace: 'pre-line', margin: 0 }}>
              {comparisonData.summary}
            </p>
          </div>

          {/* 2. TECHNICAL SIMILARITY ANALYTICS */}
          {comparisonData.technical_similarities && comparisonData.technical_similarities.length > 0 && (
            <div className="panel panel-padding" style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div>
                  <h2 className="panel-title" style={{ margin: 0 }}>
                    AI-Estimated Technical Similarity
                  </h2>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Analytical overlap aid based on shared concept coverage and IPC domain alignment.
                  </span>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
                {comparisonData.technical_similarities.map((item, idx) => (
                  <div 
                    key={idx}
                    style={{
                      background: 'var(--bg-surface-secondary)',
                      border: '1px solid var(--border-neutral)',
                      borderRadius: 'var(--border-radius-md)',
                      padding: '16px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {item.pair[0]} ↔ {item.pair[1]}
                      </span>
                      <span style={{ 
                        fontSize: '14px', 
                        fontWeight: 700, 
                        color: item.similarity_percentage >= 50 ? 'var(--primary-light)' : 'var(--text-secondary)',
                        background: 'rgba(99, 102, 241, 0.15)',
                        padding: '2px 8px',
                        borderRadius: '4px'
                      }}>
                        {item.similarity_percentage}%
                      </span>
                    </div>
                    {/* Visual Progress Bar */}
                    <div style={{ height: '6px', background: 'var(--bg-base)', borderRadius: '3px', marginBottom: '10px', overflow: 'hidden' }}>
                      <div style={{ 
                        width: `${item.similarity_percentage}%`, 
                        height: '100%', 
                        background: 'linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%)' 
                      }} />
                    </div>
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                      {item.explanation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 3. COMPARISON MATRIX */}
          <div className="panel panel-padding" style={{ marginBottom: '24px' }}>
            <h2 className="panel-title" style={{ marginBottom: '4px' }}>
              Comparison Matrix
            </h2>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Direct technical dimension mapping supported strictly by retrieved patent evidence.
            </p>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', minWidth: '700px' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border-neutral)' }}>
                    <th style={{ padding: '12px 16px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', width: '180px' }}>
                      Dimension
                    </th>
                    <th style={{ padding: '12px 10px', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', width: '110px' }}>
                      Evidence Source
                    </th>
                    {selectedPatents.map((p, idx) => (
                      <th key={idx} style={{ padding: '12px 16px', fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        Patent {String.fromCharCode(65 + idx)} ({getPatentIdentifier(p)})
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {comparisonData.matrix.map((row, rIdx) => (
                    <tr 
                      key={rIdx}
                      style={{ 
                        borderBottom: '1px solid var(--border-neutral)',
                        background: rIdx % 2 === 0 ? 'rgba(255, 255, 255, 0.01)' : 'transparent'
                      }}
                    >
                      <td style={{ padding: '12px 16px', fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {row.dimension}
                      </td>
                      <td style={{ padding: '12px 10px' }}>
                        <span style={{ 
                          fontSize: '10px', 
                          fontWeight: 600,
                          color: '#38bdf8', 
                          background: 'rgba(56, 189, 248, 0.1)', 
                          padding: '2px 6px', 
                          borderRadius: '4px' 
                        }}>
                          {row.source_evidence}
                        </span>
                      </td>
                      {selectedPatents.map((p, pIdx) => {
                        const pid = getPatentIdentifier(p);
                        const val = row.values[pid] || 'Not available in retrieved evidence.';
                        const isUnavailable = val === 'Not available in retrieved evidence.';
                        return (
                          <td 
                            key={pIdx} 
                            style={{ 
                              padding: '12px 16px', 
                              fontSize: '13px', 
                              color: isUnavailable ? 'var(--text-muted)' : 'var(--text-secondary)',
                              fontStyle: isUnavailable ? 'italic' : 'normal',
                              lineHeight: '1.5'
                            }}
                          >
                            {val}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>          {/* 4. SHARED & DISTINCT CONCEPTS */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', marginBottom: '24px' }}>
            {/* Shared Concepts */}
            <div className="panel panel-padding">
              <h2 className="panel-title" style={{ marginBottom: '8px' }}>
                Shared Technical Concepts
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                Concepts co-occurring across multiple selected patents.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {comparisonData.shared_concepts && comparisonData.shared_concepts.length > 0 ? (
                  comparisonData.shared_concepts.map((c, cIdx) => (
                    <span 
                      key={cIdx}
                      style={{
                        fontSize: '12px',
                        padding: '4px 10px',
                        background: 'rgba(99, 102, 241, 0.15)',
                        color: 'var(--primary-light)',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        borderRadius: 'var(--border-radius-sm)',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      ✓ {c}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                    No broad literal overlap identified across selected patents.
                  </span>
                )}
              </div>
            </div>

            {/* Distinct Concepts */}
            <div className="panel panel-padding">
              <h2 className="panel-title" style={{ marginBottom: '8px' }}>
                Distinct Technical Concepts
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                Distinct within the selected comparison set.
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {Object.entries(comparisonData.distinct_concepts || {}).map(([pid, concepts]) => (
                  <div key={pid}>
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', display: 'block', marginBottom: '6px' }}>
                      {pid}:
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {concepts.map((c, idx) => (
                        <span 
                          key={idx}
                          style={{
                            fontSize: '11px',
                            padding: '2px 8px',
                            background: 'var(--bg-surface-secondary)',
                            color: 'var(--text-secondary)',
                            border: '1px solid var(--border-neutral)',
                            borderRadius: '4px'
                          }}
                        >
                          • {c}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 5. KEY TECHNICAL DIFFERENCES */}
          {comparisonData.key_differences && comparisonData.key_differences.length > 0 && (
            <div className="panel panel-padding" style={{ marginBottom: '24px' }}>
              <h2 className="panel-title" style={{ marginBottom: '12px' }}>
                Key Technical Differences
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {comparisonData.key_differences.map((diff, idx) => (
                  <div 
                    key={idx}
                    style={{
                      background: 'var(--bg-surface-secondary)',
                      border: '1px solid var(--border-neutral)',
                      borderRadius: 'var(--border-radius-sm)',
                      padding: '14px 16px'
                    }}
                  >
                    <h4 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 6px 0' }}>
                      {diff.title}
                    </h4>
                    <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', margin: 0 }}>
                      {diff.difference_explanation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 6. POTENTIAL COMBINATION GAPS */}
          {comparisonData.combination_gaps && comparisonData.combination_gaps.length > 0 && (
            <div className="panel panel-padding" style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Icon name="lightbulb" size={16} color="var(--warning)" />
                <h2 className="panel-title" style={{ margin: 0 }}>
                  Potential Technology Combination Gaps
                </h2>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                Synthesized by reusing PatentIQ's innovation gap model across the selected prior-art set.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {comparisonData.combination_gaps.map((gap, idx) => (
                  <div 
                    key={idx}
                    style={{
                      background: 'rgba(234, 179, 8, 0.05)',
                      border: '1px solid rgba(234, 179, 8, 0.25)',
                      borderRadius: 'var(--border-radius-sm)',
                      padding: '14px 16px'
                    }}
                  >
                    <span style={{ 
                      fontSize: '11px', 
                      fontWeight: 700, 
                      color: 'var(--warning)', 
                      display: 'block', 
                      marginBottom: '4px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em'
                    }}>
                      Opportunity {idx + 1}
                    </span>
                    <p style={{ fontSize: '13px', color: 'var(--text-primary)', fontWeight: 500, margin: '0 0 6px 0' }}>
                      {gap.description}
                    </p>
                    <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: 0 }}>
                      <strong>Investigation Suggestion:</strong> {gap.investigation_suggestion}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* DEEP DIVE MODAL / DRAWER */}
      {deepDivePatent && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px'
          }}
          onClick={() => setDeepDivePatent(null)}
        >
          <div 
            style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-neutral)',
              borderRadius: 'var(--border-radius-lg)',
              width: '100%',
              maxWidth: '750px',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: '24px',
              boxShadow: '0 16px 40px rgba(0, 0, 0, 0.5)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--primary-light)', fontWeight: 600, textTransform: 'uppercase' }}>
                  Patent Deep-Dive Exploration
                </span>
                <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', margin: '4px 0 0 0' }}>
                  {getPatentIdentifier(deepDivePatent)}: {deepDivePatent.title}
                </h2>
              </div>
              <button 
                onClick={() => setDeepDivePatent(null)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  fontSize: '18px',
                  lineHeight: 1
                }}
              >
                ✕
              </button>
            </div>

            {isDeepDiveLoading && (
              <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
                <div style={{ fontSize: '24px', marginBottom: '10px' }}>🔍</div>
                Analyzing technical mechanisms, claims, and workflow...
              </div>
            )}

            {deepDiveError && (
              <div style={{ color: 'var(--error)', fontSize: '13px', padding: '16px 0' }}>
                <Icon name="info" size={14} color="var(--error)" /> {deepDiveError}
              </div>
            )}

            {!isDeepDiveLoading && deepDiveData && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
                {/* 1. Summary */}
                <div>
                  <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-light)', margin: '0 0 4px 0' }}>
                    1. What is this patent about?
                  </h4>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', margin: 0 }}>
                    {deepDiveData.summary}
                  </p>
                </div>

                {/* 2. Problem Addressed */}
                <div>
                  <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-light)', margin: '0 0 4px 0' }}>
                    2. Problem Addressed
                  </h4>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', margin: 0 }}>
                    {deepDiveData.problem_addressed}
                  </p>
                </div>

                {/* 3. Proposed Solution */}
                <div>
                  <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-light)', margin: '0 0 4px 0' }}>
                    3. Proposed Solution
                  </h4>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', margin: 0 }}>
                    {deepDiveData.proposed_solution}
                  </p>
                </div>

                {/* 4. Technical Workflow */}
                <div>
                  <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-light)', margin: '0 0 4px 0' }}>
                    4. Technical Workflow
                  </h4>
                  <div style={{ 
                    background: 'var(--bg-surface-secondary)', 
                    border: '1px solid var(--border-neutral)',
                    borderRadius: '4px',
                    padding: '10px 14px',
                    fontSize: '12px',
                    color: 'var(--text-primary)',
                    fontFamily: 'monospace'
                  }}>
                    {deepDiveData.technical_workflow}
                  </div>
                </div>

                {/* 5. Technologies & Methods */}
                <div>
                  <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-light)', margin: '0 0 4px 0' }}>
                    5. Supported Technologies / Methods
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {deepDiveData.technologies_methods.map((m, mIdx) => (
                      <span key={mIdx} style={{ fontSize: '11px', padding: '2px 8px', background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', borderRadius: '4px', border: '1px solid rgba(56, 189, 248, 0.25)' }}>
                        {m}
                      </span>
                    ))}
                  </div>
                </div>

                {/* 6. Distinction in Current Comparison */}
                {deepDiveData.distinction_in_set && (
                  <div>
                    <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-light)', margin: '0 0 4px 0' }}>
                      6. Distinction within Current Comparison
                    </h4>
                    <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', margin: 0 }}>
                      {deepDiveData.distinction_in_set}
                    </p>
                  </div>
                )}

                {/* 7. Claim Focus */}
                <div>
                  <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-light)', margin: '0 0 4px 0' }}>
                    7. Claim / Technical Focus
                  </h4>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', margin: 0, fontStyle: deepDiveData.claim_focus?.includes('not available') ? 'italic' : 'normal' }}>
                    {deepDiveData.claim_focus}
                  </p>
                </div>

                {/* 8. Research Questions */}
                <div>
                  <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-light)', margin: '0 0 4px 0' }}>
                    8. Research Questions for Next Steps
                  </h4>
                  <ul style={{ margin: '4px 0 0 18px', padding: 0, fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                    {deepDiveData.research_questions.map((q, qIdx) => (
                      <li key={qIdx}>{q}</li>
                    ))}
                  </ul>
                </div>

                {/* Legal Disclaimer */}
                <div style={{ 
                  marginTop: '12px',
                  padding: '8px 12px',
                  background: 'var(--bg-base)',
                  border: '1px solid var(--border-neutral)',
                  borderRadius: '4px',
                  fontSize: '11px',
                  color: 'var(--text-muted)'
                }}>
                  {deepDiveData.disclaimer}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}