import React, { useState } from 'react';
import { generateReport, getReportMarkdownUrl, getReportPdfUrl } from '../services/api';
import NoveltyGauge from '../components/NoveltyGauge';

/**
 * ReportWorkspace Component (Feature 4)
 * Dedicated workspace for configuring, generating, previewing, and exporting
 * professional PatentIQ Research Intelligence Reports as PDF and Markdown.
 */
export default function ReportWorkspace({
  onNavigate = null,
  initialTopic = '',
  initialPatents = null,
  comparisonContext = null,
  innovationContext = null
}) {
  const [topicText, setTopicText] = useState(initialTopic || '');
  const [customTitle, setCustomTitle] = useState('');
  const [sourceMode, setSourceMode] = useState('hybrid');
  const [topK, setTopK] = useState(10);
  const [includeComparison, _setIncludeComparison] = useState(true);
  const [includeInnovation, _setIncludeInnovation] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [_progressMsg, _setProgressMsg] = useState('');
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  const [activePreviewTab, setActivePreviewTab] = useState('summary'); // 'summary', 'landscape', 'patents', 'differentiation', 'all'

  // Presets for quick generation testing
  const presets = [
    {
      title: 'AI Diabetic Retinopathy Diagnostic System',
      text: 'Deep learning system for diabetic retinopathy lesion localization, microaneurysm segmentation, and severity grading on retinal fundus photography.'
    },
    {
      title: 'Decentralized Drone Swarm Collision Avoidance',
      text: 'Ultra-wideband relative localization with edge optical flow and mesh consensus protocols for autonomous aerial drone swarm navigation.'
    },
    {
      title: 'Wearable PPG Biometric Authentication Protocol',
      text: 'Zero-knowledge continuous biometric identity verification using arterial pulse waveform dynamics and hardware secure enclave key generation.'
    }
  ];

  const handleGenerate = async (overrideText = null) => {
    const text = (overrideText !== null ? overrideText : topicText).trim();
    if (!text && !initialPatents) {
      setError('Please provide an invention description or select available research results to generate a report.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setProgressMsg('Collecting available research analysis and evaluating evidence...');

    try {
      const response = await generateReport({
        title: customTitle.trim() || undefined,
        inventionDescription: text || undefined,
        query: text || undefined,
        sourceMode,
        topK,
        includeComparison,
        includeInnovation,
        comparisonResults: comparisonContext,
        innovationResults: innovationContext,
        searchResults: initialPatents
      });
      setReport(response);
      setIsLoading(false);
    } catch (err) {
      console.error('Report generation error:', err);
      setError(err.message || 'Report generation failed. Please try again.');
      setIsLoading(false);
    }
  };

  const _getCoverageColor = (status) => {
    switch (status) {
      case 'Strongly Represented': return '#ef4444';
      case 'Moderately Represented': return '#f59e0b';
      case 'Weakly Represented': return '#3b82f6';
      case 'Minimally Represented': return '#10b981';
      default: return 'var(--text-muted)';
    }
  };

  return (
    <div className="container" style={{ paddingBottom: '90px' }}>
      {/* 1. Header Section */}
      <div style={{ marginBottom: '28px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span style={{ fontSize: '24px' }}>📋</span>
              <h1 style={{ fontSize: '26px', fontWeight: 700, margin: 0 }}>Research Intelligence Reports</h1>
              <span className="badge badge-neutral" style={{ fontSize: '11px', textTransform: 'uppercase' }}>Feature 4</span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', maxWidth: '850px', margin: 0 }}>
              Consolidate prior-art search results, multi-patent comparisons, and innovation refinement analyses into
              a verified research intelligence report with exportable PDF and Markdown documents.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {onNavigate && (
              <button className="btn btn-secondary" onClick={() => onNavigate('copilot')} style={{ fontSize: '13px' }}>
                🤖 Ask Copilot
              </button>
            )}
            {onNavigate && (
              <button className="btn btn-secondary" onClick={() => onNavigate('compare')} style={{ fontSize: '13px' }}>
                Compare Patents
              </button>
            )}
            {onNavigate && (
              <button className="btn btn-secondary" onClick={() => onNavigate('innovation')} style={{ fontSize: '13px' }}>
                💡 Innovation Refinement
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 2. Setup & Configuration Card */}
      <div className="panel panel-padding" style={{ marginBottom: '28px', background: 'var(--bg-surface)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, margin: 0, color: 'var(--text-primary)' }}>
            Configure Research Intelligence Report
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Source Mode:</span>
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
                    fontWeight: sourceMode === src.id ? 600 : 400
                  }}
                >
                  {src.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '14px' }}>
          <div>
            <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
              Custom Report Title (Optional)
            </label>
            <input
              type="text"
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              placeholder="e.g. Prior-Art Intelligence: AI Retinal Screening"
              style={{
                width: '100%',
                padding: '10px 12px',
                background: 'var(--bg-surface-secondary)',
                border: '1px solid var(--border-neutral)',
                borderRadius: 'var(--border-radius-sm)',
                color: 'var(--text-primary)',
                fontSize: '13px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
              Corpus Evaluation Depth: {topK} Documents
            </label>
            <input
              type="range"
              min={5}
              max={25}
              step={5}
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value, 10))}
              style={{ width: '100%', marginTop: '8px' }}
            />
          </div>
        </div>

        <div style={{ marginBottom: '14px' }}>
          <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
            Invention Topic or Research Objective
          </label>
          <textarea
            rows={3}
            value={topicText}
            onChange={(e) => setTopicText(e.target.value)}
            placeholder="Describe your technical invention or research objective (e.g. 'Deep learning system for diabetic retinopathy lesion localization, microaneurysm segmentation, and severity grading on retinal fundus photography...')"
            style={{
              width: '100%',
              padding: '12px',
              background: 'var(--bg-surface-secondary)',
              border: '1px solid var(--border-neutral)',
              borderRadius: 'var(--border-radius-sm)',
              color: 'var(--text-primary)',
              fontSize: '13px',
              lineHeight: 1.5,
              resize: 'vertical'
            }}
          />
        </div>

        {/* Quick Example Presets */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Quick Presets:
            </span>
            {presets.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setCustomTitle(p.title);
                  setTopicText(p.text);
                  handleGenerate(p.text);
                }}
                style={{
                  background: 'var(--bg-surface-secondary)',
                  border: '1px solid var(--border-neutral)',
                  color: 'var(--text-secondary)',
                  padding: '4px 10px',
                  borderRadius: 'var(--border-radius-sm)',
                  fontSize: '11px',
                  cursor: 'pointer'
                }}
              >
                {p.title.split(' ')[1] || p.title}
              </button>
            ))}
          </div>

          <button
            className="btn btn-primary"
            onClick={() => handleGenerate()}
            disabled={isLoading || (!topicText.trim() && !initialPatents)}
            style={{ minWidth: '220px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
          >
            {isLoading ? (
              <>
                <span className="loading-spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></span>
                <span>Assembling Report...</span>
              </>
            ) : (
              <>
                <span>📋</span>
                <span>Generate Intelligence Report</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div style={{ marginTop: '14px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--error)', borderRadius: 'var(--border-radius-sm)', color: 'var(--text-primary)', fontSize: '13px' }}>
            <strong>Generation Notice:</strong> {error}
          </div>
        )}
      </div>

      {/* 3. Generated Report Viewport */}
      {report && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
          {/* Action & Metadata Header Banner */}
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', borderLeft: '4px solid var(--primary)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary-light)', fontSize: '11px' }}>
                    {report.report_id}
                  </span>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Generated: {report.generated_at}
                  </span>
                </div>
                <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                  {report.title}
                </h2>
              </div>

              {/* Direct Export Action Buttons */}
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <a
                  href={getReportPdfUrl(report.report_id)}
                  download={`${report.report_id}.pdf`}
                  className="btn btn-primary"
                  style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}
                >
                  <span>📥</span>
                  <span>Export PDF</span>
                </a>
                <a
                  href={getReportMarkdownUrl(report.report_id)}
                  download={`${report.report_id}.md`}
                  className="btn btn-secondary"
                  style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}
                >
                  <span>📄</span>
                  <span>Export Markdown</span>
                </a>
              </div>
            </div>
          </div>

          {/* Section Navigation Tabs */}
          <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '8px', overflowX: 'auto' }}>
            {[
              { id: 'summary', label: 'Executive Summary' },
              { id: 'landscape', label: `Prior-Art Landscape (${report.prior_art_landscape?.length || 0})` },
              { id: 'patents', label: `Detailed Summaries (${report.detailed_patent_summaries?.length || 0})` },
              { id: 'comparison', label: `Comparison (${report.patent_comparison ? report.patent_comparison.compared_patents?.length : 0})` },
              { id: 'differentiation', label: `Differentiation (${report.differentiation_directions?.length || 0})` },
              { id: 'all', label: 'Full Intelligence View' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActivePreviewTab(tab.id)}
                style={{
                  background: activePreviewTab === tab.id ? 'var(--primary)' : 'var(--bg-surface)',
                  color: activePreviewTab === tab.id ? '#ffffff' : 'var(--text-secondary)',
                  border: '1px solid var(--border-neutral)',
                  padding: '6px 14px',
                  borderRadius: 'var(--border-radius-sm)',
                  fontSize: '12px',
                  fontWeight: activePreviewTab === tab.id ? 600 : 400,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* SECTION: Executive Summary & Objective */}
          {(activePreviewTab === 'summary' || activePreviewTab === 'all') && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '10px', color: 'var(--text-primary)' }}>
                  1. Executive Summary
                </h3>
                <p style={{ fontSize: '13.5px', color: 'var(--text-primary)', lineHeight: 1.6, marginBottom: '16px' }}>
                  {report.executive_summary.overview}
                </p>

                <div style={{ marginBottom: '14px' }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    Key Intelligence Observations:
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {report.executive_summary.key_findings.map((kf, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                        <span style={{ color: 'var(--primary-light)', fontWeight: 700 }}>•</span>
                        <span>{kf}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px', marginTop: '16px' }}>
                  <div style={{ background: 'var(--bg-surface-secondary)', padding: '12px', borderRadius: 'var(--border-radius-sm)', border: '1px solid var(--border-neutral)' }}>
                    <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>
                      Prior-Art Saturation Overview
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {report.executive_summary.novelty_summary}
                    </div>
                  </div>
                  <div style={{ background: 'var(--bg-surface-secondary)', padding: '12px', borderRadius: 'var(--border-radius-sm)', border: '1px solid var(--border-neutral)' }}>
                    <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>
                      Differentiation Potential
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {report.executive_summary.differentiation_summary}
                    </div>
                  </div>
                </div>
              </div>

              {/* Research Objective Card */}
              <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
                <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                  2. Research Objective & Evaluated Scope
                </h3>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '10px' }}>
                  <strong>Objective: </strong> {report.research_objective.statement}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  Domain: {report.research_objective.technical_domain} |
                  Evaluated Corpus: {report.methodology.total_patents_evaluated} documents ({report.provenance.primary_source})
                </div>
              </div>
            </div>
          )}

          {/* SECTION: Prior-Art Landscape Table */}
          {(activePreviewTab === 'landscape' || activePreviewTab === 'all') && (
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px', color: 'var(--text-primary)' }}>
                3. Prior-Art Landscape ({report.prior_art_landscape?.length} Documents)
              </h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12.5px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-neutral)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '11px', textTransform: 'uppercase' }}>
                      <th style={{ padding: '8px 10px' }}>Publication #</th>
                      <th style={{ padding: '8px 10px' }}>Title</th>
                      <th style={{ padding: '8px 10px' }}>Applicant</th>
                      <th style={{ padding: '8px 10px' }}>Date</th>
                      <th style={{ padding: '8px 10px' }}>Relevance</th>
                      <th style={{ padding: '8px 10px' }}>Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.prior_art_landscape?.map((pa, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '10px', fontFamily: 'monospace', fontWeight: 600, color: 'var(--primary-light)' }}>
                          {pa.publication_number}
                        </td>
                        <td style={{ padding: '10px', color: 'var(--text-primary)', maxWidth: '280px' }}>
                          {pa.title}
                        </td>
                        <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>
                          {pa.applicant}
                        </td>
                        <td style={{ padding: '10px', color: 'var(--text-muted)' }}>
                          {pa.publication_date || '—'}
                        </td>
                        <td style={{ padding: '10px', fontWeight: 600 }}>
                          {Math.round(pa.relevance_score <= 1.0 ? pa.relevance_score * 100 : pa.relevance_score)}%
                        </td>
                        <td style={{ padding: '10px', color: 'var(--text-muted)', fontSize: '11px' }}>
                          {pa.source}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION: Detailed Patent Summaries */}
          {(activePreviewTab === 'patents' || activePreviewTab === 'all') && (
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', color: 'var(--text-primary)' }}>
                4. Detailed Patent Technical Summaries
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {report.detailed_patent_summaries?.map((ps, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'var(--bg-surface-secondary)',
                      border: '1px solid var(--border-neutral)',
                      borderRadius: 'var(--border-radius-md)',
                      padding: '16px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '8px' }}>
                      <div>
                        <span style={{ fontFamily: 'monospace', fontWeight: 700, color: 'var(--primary-light)', fontSize: '13px', marginRight: '8px' }}>
                          {ps.publication_number}
                        </span>
                        <strong style={{ color: 'var(--text-primary)', fontSize: '14px' }}>{ps.title}</strong>
                      </div>
                      <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
                        {ps.evidence_source}
                      </span>
                    </div>

                    <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '8px' }}>
                      <strong style={{ color: 'var(--text-primary)' }}>Core Technical Idea: </strong>
                      {ps.core_technical_idea}
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
                      <div><strong>Problem: </strong> {ps.problem_addressed}</div>
                      <div><strong>Relevance: </strong> {ps.relevance_to_objective}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SECTION: Multi-Patent Comparison */}
          {(activePreviewTab === 'comparison' || activePreviewTab === 'all') && report.patent_comparison && (
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px', color: 'var(--text-primary)' }}>
                5. Multi-Patent Technical Comparison
              </h3>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '10px' }}>
                Compared Documents: {report.patent_comparison.compared_patents.join(', ')}
              </div>
              {report.patent_comparison.shared_concepts?.length > 0 && (
                <div style={{ marginBottom: '12px' }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
                    Shared Concepts:
                  </div>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {report.patent_comparison.shared_concepts.map((c, idx) => (
                      <span key={idx} className="badge badge-neutral" style={{ fontSize: '11px' }}>{c}</span>
                    ))}
                  </div>
                </div>
              )}
              {report.patent_comparison.technical_differences?.length > 0 && (
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
                    Technical Differences:
                  </div>
                  {report.patent_comparison.technical_differences.map((d, idx) => (
                    <div key={idx} style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                      • {d}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* SECTION: Differentiation Directions & Questions */}
          {(activePreviewTab === 'differentiation' || activePreviewTab === 'all') && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {/* Novelty Gauge & Coverage Summary */}
              {report.novelty_indicator && (
                <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', alignItems: 'center' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <NoveltyGauge score={report.novelty_indicator.overall_novelty_score} />
                    <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '6px' }}>
                      {report.novelty_indicator.overall_novelty_score}/100 ({report.novelty_indicator.band})
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      AI-Estimated Novelty Indicator
                    </div>
                  </div>
                  <div>
                    <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>
                      Prior-Art Saturation Analysis
                    </h4>
                    <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                      {report.novelty_indicator.explanation}
                    </p>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>
                      * {report.novelty_indicator.disclaimer}
                    </div>
                  </div>
                </div>
              )}

              {/* Differentiation Directions Cards */}
              {report.differentiation_directions?.length > 0 && (
                <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', color: 'var(--text-primary)' }}>
                    Technical Differentiation Directions ({report.differentiation_directions.length})
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {report.differentiation_directions.map((dir, idx) => (
                      <div
                        key={idx}
                        style={{
                          background: 'var(--bg-surface-secondary)',
                          border: '1px solid var(--border-neutral)',
                          borderRadius: 'var(--border-radius-md)',
                          padding: '14px'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '6px', marginBottom: '6px' }}>
                          <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                            [{dir.category}] {dir.direction}
                          </span>
                          <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
                            {dir.evidence_gap_level}
                          </span>
                        </div>
                        <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '8px' }}>
                          <strong>Why Investigate: </strong> {dir.why_investigate}
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--primary-light)', fontStyle: 'italic', background: 'rgba(99, 102, 241, 0.08)', padding: '8px 12px', borderRadius: '4px' }}>
                          Research Question: "{dir.research_question}"
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Empirical Research Questions */}
              {report.research_questions?.length > 0 && (
                <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '10px', color: 'var(--text-primary)' }}>
                    Empirical Research Questions
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {report.research_questions.map((rq, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                        <span style={{ color: 'var(--primary)', fontWeight: 700 }}>{idx + 1}.</span>
                        <span>{rq}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* SECTION: Limitations & Legal Disclaimer */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              <strong style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
                Methodology & Corpus Limitations:
              </strong>
              {report.limitations?.dataset_coverage}
            </div>

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
              <strong>Mandatory Legal Notice: </strong> {report.disclaimer}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
