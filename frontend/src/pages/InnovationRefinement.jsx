import React, { useState, useEffect } from 'react';
import { analyzeInnovation } from '../services/api';
import PatentCard from '../components/PatentCard';
import NoveltyGauge from '../components/NoveltyGauge';

/**
 * InnovationRefinement Component (Feature 3)
 * Dedicated workspace for researching idea refinement, concept coverage landscape,
 * combination gaps, grounded technical differentiation directions, and empirical research questions.
 */
export default function InnovationRefinement({
  onNavigate = null,
  initialIdea = '',
  comparisonContext = null
}) {
  const [ideaText, setIdeaText] = useState(initialIdea || '');
  const [sourceMode, setSourceMode] = useState('hybrid');
  const [activeView, setActiveView] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [highlightedPatentId, setHighlightedPatentId] = useState(null);

  const presets = [
    {
      title: 'AI Diabetic Retinopathy',
      text: 'An AI system for detecting diabetic retinopathy from retinal fundus images using deep learning, lesion localization, microaneurysm segmentation, and severity grading.'
    },
    {
      title: 'Autonomous Swarm Navigation',
      text: 'A decentralized swarm navigation system for aerial drones using ultra-wideband relative localization, edge optical flow, and mesh consensus collision avoidance.'
    },
    {
      title: 'Biometric Cryptographic Auth',
      text: 'A continuous zero-knowledge biometric authentication protocol on wearable sensors using PPG arterial pulse waveforms and hardware secure enclave key generation.'
    }
  ];

  useEffect(() => {
    if (initialIdea && initialIdea.trim().split(/\s+/).length >= 4 && !result && !isLoading) {
      handleAnalyze(initialIdea);
    }
  }, [initialIdea]);

  const handleAnalyze = async (textToAnalyze = null) => {
    const text = (textToAnalyze !== null ? textToAnalyze : ideaText).trim();
    if (!text) {
      setError('Please provide a description of your innovation or technical idea.');
      return;
    }
    if (text.split(/\s+/).length < 3) {
      setError('Please provide at least 3-4 words describing your invention or technical approach.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await analyzeInnovation({
        idea: text,
        sourceMode,
        topK: 10,
        comparisonContext: comparisonContext
      });
      setResult(response);
      setIsLoading(false);
    } catch (err) {
      console.error('Innovation analysis error:', err);
      setError(err.message || 'Innovation refinement analysis failed. Please try again.');
      setIsLoading(false);
    }
  };

  const getCoverageColor = (status) => {
    switch (status) {
      case 'Strongly Represented': return '#ef4444';
      case 'Moderately Represented': return '#f59e0b';
      case 'Weakly Represented': return '#3b82f6';
      case 'Minimally Represented': return '#10b981';
      case 'No Meaningful Evidence': return '#8b5cf6';
      default: return 'var(--text-muted)';
    }
  };

  const getGapColor = (gapLevel) => {
    switch (gapLevel) {
      case 'HIGHER EVIDENCE GAP': return 'var(--success)';
      case 'MODERATE EVIDENCE GAP': return '#3b82f6';
      case 'WEAK EVIDENCE GAP': return 'var(--warning)';
      case 'INSUFFICIENT EVIDENCE': return 'var(--text-muted)';
      default: return 'var(--primary)';
    }
  };

  const filterDirections = () => {
    if (!result || !result.differentiation_directions) return [];
    if (categoryFilter === 'All') return result.differentiation_directions;
    return result.differentiation_directions.filter(d => d.category === categoryFilter);
  };

  const filteredDirections = filterDirections();
  const categories = ['All', 'Technical Architecture', 'Data / Input', 'Processing Pipeline', 'AI / ML Methods', 'System Combination'];

  return (
    <div className="container" style={{ paddingBottom: '80px' }}>
      {/* 1. Header Section */}
      <div style={{ marginBottom: '28px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span style={{ fontSize: '24px' }}>💡</span>
              <h1 style={{ fontSize: '26px', fontWeight: 700, margin: 0 }}>Innovation Refinement & Differentiation</h1>
              <span className="badge badge-neutral" style={{ fontSize: '11px', textTransform: 'uppercase' }}>Feature 3</span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', maxWidth: '850px', margin: 0 }}>
              Explore how your idea compares with the retrieved prior-art landscape and identify technical directions worth investigating.
              Empirical research intelligence grounded in indexed Indian patents and EPO documents.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {onNavigate && (
              <button
                className="btn btn-secondary"
                onClick={() => onNavigate('copilot')}
                style={{ fontSize: '13px' }}
              >
                🤖 Ask Copilot
              </button>
            )}
            {onNavigate && (
              <button
                className="btn btn-secondary"
                onClick={() => onNavigate('compare')}
                style={{ fontSize: '13px' }}
              >
                Compare Patents
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 2. Idea Input Workspace */}
      <div className="panel panel-padding" style={{ marginBottom: '28px', background: 'var(--bg-surface)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '10px' }}>
          <label style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
            Describe Your Innovation or Technical Idea
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Retrieval Source:</span>
            <div style={{ display: 'flex', background: 'var(--bg-surface-secondary)', borderRadius: 'var(--border-radius-sm)', padding: '2px', border: '1px solid var(--border-neutral)' }}>
              {[
                { id: 'hybrid', label: 'Hybrid (Local + EPO)' },
                { id: 'local', label: 'Local Only' },
                { id: 'live', label: 'EPO Live EPS' }
              ].map(src => (
                <button
                  key={src.id}
                  onClick={() => setSourceMode(src.id)}
                  style={{
                    background: sourceMode === src.id ? 'var(--primary)' : 'transparent',
                    color: sourceMode === src.id ? '#ffffff' : 'var(--text-secondary)',
                    border: 'none',
                    padding: '4px 10px',
                    fontSize: '11px',
                    borderRadius: 'var(--border-radius-sm)',
                    cursor: 'pointer',
                    fontWeight: sourceMode === src.id ? 600 : 400,
                    transition: 'all var(--transition-fast)'
                  }}
                >
                  {src.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <textarea
          rows={4}
          value={ideaText}
          onChange={(e) => setIdeaText(e.target.value)}
          placeholder="Describe your invention, system, technical approach, or research idea naturally (e.g. 'I am building an AI system that detects diabetic retinopathy from retinal fundus images using deep learning, lesion localization, and severity grading...')"
          style={{
            width: '100%',
            padding: '14px',
            background: 'var(--bg-surface-secondary)',
            border: '1px solid var(--border-neutral)',
            borderRadius: 'var(--border-radius-md)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            lineHeight: '1.6',
            resize: 'vertical',
            fontFamily: 'var(--font-body)',
            marginBottom: '14px',
            outline: 'none'
          }}
        />

        {/* Quick Presets & Action Row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Quick Examples:
            </span>
            {presets.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setIdeaText(preset.text);
                  handleAnalyze(preset.text);
                }}
                style={{
                  background: 'var(--bg-surface-secondary)',
                  border: '1px solid var(--border-neutral)',
                  color: 'var(--text-secondary)',
                  padding: '4px 10px',
                  borderRadius: 'var(--border-radius-sm)',
                  fontSize: '12px',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)'
                }}
              >
                {preset.title}
              </button>
            ))}
          </div>

          <button
            className="btn btn-primary"
            onClick={() => handleAnalyze()}
            disabled={isLoading || !ideaText.trim()}
            style={{ minWidth: '170px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
          >
            {isLoading ? (
              <>
                <span className="loading-spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></span>
                <span>Analyzing Prior Art...</span>
              </>
            ) : (
              <>
                <span>💡</span>
                <span>Analyze Innovation</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div style={{ marginTop: '16px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--error)', borderRadius: 'var(--border-radius-sm)', color: 'var(--text-primary)', fontSize: '13px' }}>
            <strong>Analysis Notice:</strong> {error}
          </div>
        )}
      </div>

      {/* 3. Results Section */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Summary Overview Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
            {/* Left Card: Innovation & Corpus Summary */}
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span className="badge badge-neutral" style={{ fontSize: '11px' }}>Innovation Summary</span>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {result.retrieved_patents?.length || 0} Prior-Art Matches
                  </span>
                </div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                  {result.idea_summary}
                </h3>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '12px' }}>
                  <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
                    Source: {result.provenance?.primary_source || 'Federated Retrieval'}
                  </span>
                  {result.provenance?.local_count > 0 && (
                    <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
                      Indian Corpus: {result.provenance.local_count}
                    </span>
                  )}
                  {result.provenance?.live_count > 0 && (
                    <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
                      EPO EPS: {result.provenance.live_count}
                    </span>
                  )}
                </div>
              </div>

              <div style={{ marginTop: '20px', padding: '12px', background: 'var(--bg-surface-secondary)', borderRadius: 'var(--border-radius-sm)', borderLeft: '3px solid var(--primary)' }}>
                <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>
                  Research Guidance
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  Based on the retrieved prior-art set, explore below which concepts are saturated and which architectural combinations offer differentiated investigation opportunities.
                </div>
              </div>
            </div>

            {/* Right Card: AI-Estimated Novelty Indicator */}
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span className="badge badge-neutral" style={{ fontSize: '11px' }}>Prior-Art Similarity</span>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {result.novelty_indicator?.band || 'Moderate Differentiation'}
                </span>
              </div>

              <NoveltyGauge score={result.novelty_indicator?.overall_novelty_score || 50} />

              <div style={{ fontSize: '18px', fontWeight: 700, marginTop: '8px', color: 'var(--text-primary)' }}>
                {result.novelty_indicator?.overall_novelty_score || 50} / 100
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px', textAlign: 'center' }}>
                AI-Estimated Novelty Indicator
              </div>

              <div style={{ marginTop: '12px', fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.4 }}>
                Automated similarity metric based on retrieved dataset. Not a legal determination of novelty or patentability.
              </div>
            </div>
          </div>

          {/* View Selection Tabs */}
          <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '8px', overflowX: 'auto' }}>
            {[
              { id: 'all', label: 'All Analysis Views' },
              { id: 'coverage', label: `Concept Landscape (${result.concept_coverage?.length || 0})` },
              { id: 'directions', label: `Differentiation Directions (${result.differentiation_directions?.length || 0})` },
              { id: 'gaps', label: `Combination Gaps (${result.combination_gaps?.length || 0})` },
              { id: 'questions', label: `Research Questions (${result.research_questions?.length || 0})` },
              { id: 'patents', label: `Relevant Prior Art (${result.retrieved_patents?.length || 0})` }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id)}
                style={{
                  background: activeView === tab.id ? 'var(--primary)' : 'var(--bg-surface)',
                  color: activeView === tab.id ? '#ffffff' : 'var(--text-secondary)',
                  border: '1px solid var(--border-neutral)',
                  padding: '6px 14px',
                  borderRadius: 'var(--border-radius-sm)',
                  fontSize: '12px',
                  fontWeight: activeView === tab.id ? 600 : 400,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all var(--transition-fast)'
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* VIEW: Concept Coverage Landscape & Idea vs Prior Art */}
          {(activeView === 'all' || activeView === 'coverage') && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Concept Coverage Cards */}
              <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>
                      Concept Coverage Landscape (Retrieved Prior Art)
                    </h3>
                    <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                      Representation intensity of technical concepts across the retrieved prior-art set.
                    </p>
                  </div>
                  <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
                    {result.concept_coverage?.length || 0} Concepts Analyzed
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
                  {result.concept_coverage?.map((c, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'var(--bg-surface-secondary)',
                        border: '1px solid var(--border-neutral)',
                        borderRadius: 'var(--border-radius-md)',
                        padding: '14px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between'
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                          <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                            {c.concept}
                          </span>
                          <span
                            style={{
                              fontSize: '11px',
                              fontWeight: 600,
                              color: getCoverageColor(c.status),
                              background: 'rgba(255,255,255,0.05)',
                              padding: '2px 8px',
                              borderRadius: '4px'
                            }}
                          >
                            {c.status}
                          </span>
                        </div>
                        {/* Progress Bar */}
                        <div style={{ height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden', marginBottom: '10px' }}>
                          <div
                            style={{
                              width: `${Math.round(c.max_similarity * 100)}%`,
                              height: '100%',
                              backgroundColor: getCoverageColor(c.status),
                              borderRadius: '3px'
                            }}
                          />
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                          Coverage Intensity: {Math.round(c.max_similarity * 100)}%
                        </div>
                      </div>

                      {c.representative_patents?.length > 0 && (
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                          Prior Art: {c.representative_patents.join(', ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Your Idea vs Retrieved Prior Art Table */}
              <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '6px' }}>
                  Your Idea vs Retrieved Prior Art Mapping
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  Visual comparison comparing user concepts against representation evidence in the retrieved set.
                </p>

                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-neutral)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '11px', textTransform: 'uppercase' }}>
                        <th style={{ padding: '10px 12px' }}>Your Idea Concept</th>
                        <th style={{ padding: '10px 12px' }}>Prior Art Status</th>
                        <th style={{ padding: '10px 12px' }}>Differentiation Opportunity</th>
                        <th style={{ padding: '10px 12px' }}>Representative Patent</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.idea_vs_prior_art?.map((item, idx) => (
                        <tr
                          key={idx}
                          style={{
                            borderBottom: '1px solid rgba(255,255,255,0.04)',
                            transition: 'background var(--transition-fast)'
                          }}
                        >
                          <td style={{ padding: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                            {item.concept}
                          </td>
                          <td style={{ padding: '12px' }}>
                            <span style={{
                              color: item.prior_art_status.startsWith('✓') ? '#ef4444' : item.prior_art_status.startsWith('~') ? '#f59e0b' : '#10b981',
                              fontWeight: 600
                            }}>
                              {item.prior_art_status}
                            </span>
                          </td>
                          <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>
                            {item.differentiation_potential}
                          </td>
                          <td style={{ padding: '12px', color: 'var(--text-muted)', fontFamily: 'monospace', fontSize: '12px' }}>
                            {item.representative_patent || '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* VIEW: Differentiation Directions */}
          {(activeView === 'all' || activeView === 'directions') && (
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
                <div>
                  <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>
                    Technical Differentiation Directions
                  </h3>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                    Actionable research directions where technical modifications may diverge from existing prior-art saturation.
                  </p>
                </div>

                {/* Category Filter Pills */}
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {categories.map(cat => (
                    <button
                      key={cat}
                      onClick={() => setCategoryFilter(cat)}
                      style={{
                        background: categoryFilter === cat ? 'var(--primary)' : 'var(--bg-surface-secondary)',
                        color: categoryFilter === cat ? '#ffffff' : 'var(--text-secondary)',
                        border: '1px solid var(--border-neutral)',
                        padding: '4px 10px',
                        borderRadius: 'var(--border-radius-sm)',
                        fontSize: '11px',
                        cursor: 'pointer',
                        transition: 'all var(--transition-fast)'
                      }}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              {filteredDirections.length === 0 ? (
                <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No differentiation directions found for category: {categoryFilter}
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {filteredDirections.map((dir, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'var(--bg-surface-secondary)',
                        border: '1px solid var(--border-neutral)',
                        borderRadius: 'var(--border-radius-md)',
                        padding: '18px',
                        transition: 'border-color var(--transition-fast)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary-light)', fontSize: '11px' }}>
                              {dir.category}
                            </span>
                            <span className="badge" style={{ background: 'rgba(255,255,255,0.06)', color: getGapColor(dir.evidence_gap_level), fontSize: '11px' }}>
                              {dir.evidence_gap_level}
                            </span>
                          </div>
                          <h4 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                            {dir.direction}
                          </h4>
                        </div>
                      </div>

                      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '12px' }}>
                        <strong style={{ color: 'var(--text-primary)' }}>Why investigate: </strong>
                        {dir.why_investigate}
                      </div>

                      {/* Research Question */}
                      <div style={{ padding: '10px 14px', background: 'rgba(0,0,0,0.2)', borderRadius: 'var(--border-radius-sm)', borderLeft: '3px solid #3b82f6', marginBottom: '12px' }}>
                        <div style={{ fontSize: '11px', color: '#60a5fa', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>
                          Research Question
                        </div>
                        <div style={{ fontSize: '13px', color: 'var(--text-primary)', fontStyle: 'italic' }}>
                          "{dir.research_question}"
                        </div>
                      </div>

                      {/* Related Concepts & Evidence */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                        <div>
                          <span>Related concepts: </span>
                          <span style={{ color: 'var(--text-secondary)' }}>
                            {dir.related_concepts?.join(', ') || 'General architecture'}
                          </span>
                        </div>
                        {dir.linked_patent_ids?.length > 0 && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span>Linked Evidence:</span>
                            {dir.linked_patent_ids.map(pid => (
                              <span
                                key={pid}
                                onClick={() => {
                                  setActiveView('patents');
                                  setHighlightedPatentId(pid);
                                }}
                                style={{
                                  color: 'var(--primary-light)',
                                  cursor: 'pointer',
                                  textDecoration: 'underline'
                                }}
                              >
                                {pid}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* VIEW: Potential Combination Gaps */}
          {(activeView === 'all' || activeView === 'gaps') && (
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <div>
                  <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>
                    Potential Combination Gaps
                  </h3>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                    Individually known concepts where joint pairwise representation appears limited in the retrieved art.
                  </p>
                </div>
                <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
                  {result.combination_gaps?.length || 0} Identified
                </span>
              </div>

              {result.combination_gaps?.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No distinct combination gaps identified in the current retrieved set.
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '14px' }}>
                  {result.combination_gaps.map((gap, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'var(--bg-surface-secondary)',
                        border: '1px solid var(--border-neutral)',
                        borderRadius: 'var(--border-radius-md)',
                        padding: '14px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                        <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                          {gap.gap_title || gap.concept || 'Pairwise Combination Gap'}
                        </span>
                        <span className="badge badge-neutral" style={{ fontSize: '10px' }}>
                          Joint Overlap: {gap.joint_saturation ?? 'Low'}
                        </span>
                      </div>
                      <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: '0 0 10px 0' }}>
                        {gap.rationale || gap.description || 'Concepts are individually represented in prior art, but their co-occurrence in a single system is minimally documented.'}
                      </p>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        Status: Potential Architectural Gap (Research Only)
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* VIEW: Empirical Research Questions */}
          {(activeView === 'all' || activeView === 'questions') && (
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '6px' }}>
                Empirical Research Questions
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                Key technical questions researchers can investigate during prototyping and experimental validation.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {result.research_questions?.map((q, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '12px',
                      background: 'var(--bg-surface-secondary)',
                      padding: '12px 16px',
                      borderRadius: 'var(--border-radius-sm)',
                      border: '1px solid var(--border-neutral)'
                    }}
                  >
                    <span style={{ color: 'var(--primary)', fontWeight: 700, fontSize: '14px' }}>
                      {idx + 1}.
                    </span>
                    <span style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                      {q}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* VIEW: Relevant Prior Art Matches */}
          {(activeView === 'all' || activeView === 'patents') && (
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>
                    Relevant Prior-Art Corpus Matches
                  </h3>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                    Ranked prior-art patents retrieved from the indexed repository and live EPO endpoints.
                  </p>
                </div>
                <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
                  {result.retrieved_patents?.length || 0} Retrieved
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {result.retrieved_patents?.map((patent, idx) => {
                  const pid = patent.publication_number || patent.application_number;
                  const isHighlighted = highlightedPatentId === pid;

                  return (
                    <div
                      key={idx}
                      id={`patent-${pid}`}
                      style={{
                        outline: isHighlighted ? '2px solid var(--primary)' : 'none',
                        borderRadius: 'var(--border-radius-md)'
                      }}
                    >
                      <PatentCard
                        patent={patent}
                        selectable={false}
                        highlightClass={isHighlighted ? 'highlighted-patent' : ''}
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* 4. Mandatory Legal Disclaimer */}
          <div
            style={{
              padding: '16px 20px',
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-neutral)',
              borderRadius: 'var(--border-radius-md)',
              fontSize: '12px',
              color: 'var(--text-muted)',
              lineHeight: 1.6
            }}
          >
            <strong>Research Notice & Legal Disclaimer:</strong> {result.disclaimer || 'This analysis is based on the retrieved prior-art set and is intended for technical research and refinement purposes only. It is NOT a legal determination of patentability, patent validity, or novelty, and does not guarantee that no other patent exists.'}
          </div>
        </div>
      )}
    </div>
  );
}
