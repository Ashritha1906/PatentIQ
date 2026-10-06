import React, { useState } from 'react';

export default function PatentCard({ patent, highlightClass = '' }) {
  const [expanded, setExpanded] = useState(false);

  // Extract publication/application year from application number or metadata
  const appNum = patent.publication_number || patent.application_number || patent.patent_id || '';
  const getYear = () => {
    if (patent.publication_date) {
      const match = patent.publication_date.match(/\b(19|20)\d{2}\b/);
      if (match) return match[0];
    }
    const match = appNum.match(/\b(19|20)\d{2}\b/);
    return match ? match[0] : null;
  };

  const year = getYear();
  const applicant = patent.applicant || patent.applicant_name || 'Unknown Applicant';
  const classification = patent.classification || patent.classification_ipc || 'Unknown IPC';
  const source = patent.source || 'PatentIQ Indexed Corpus';

  // Color helper for scores
  const getScoreColorClass = (score) => {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
  };

  const simPercent = Math.round((patent.semantic_score ?? patent.similarity_score ?? 0) * 100);
  const kwPercent = patent.keyword_score !== undefined ? Math.round(patent.keyword_score * 100) : null;
  const finalPercent = patent.final_score !== undefined ? Math.round(patent.final_score * 100) : null;

  return (
    <div 
      className={`panel interactive panel-padding ${highlightClass}`} 
      id={`patent-${appNum.replace(/[^a-zA-Z0-9]/g, '-')}`}
      style={{
        marginBottom: '16px',
        transition: 'all var(--transition-normal)',
        borderLeft: highlightClass ? '3px solid var(--primary)' : '1px solid var(--border-neutral)'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '280px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>
              {appNum} {year ? `• ${year}` : ''}
            </span>
            <span style={{ 
              fontSize: '10px', 
              fontWeight: 600,
              color: source.includes('EPO') && source.includes('LOCAL') ? '#c084fc' : source.includes('EPO') ? '#38bdf8' : 'var(--primary-light)', 
              background: source.includes('EPO') && source.includes('LOCAL') ? 'rgba(192, 132, 252, 0.15)' : source.includes('EPO') ? 'rgba(56, 189, 248, 0.15)' : 'rgba(59, 130, 246, 0.1)', 
              padding: '2px 8px', 
              borderRadius: '4px',
              border: '1px solid ' + (source.includes('EPO') ? 'rgba(56, 189, 248, 0.3)' : 'rgba(59, 130, 246, 0.2)')
            }}>
              {source === 'EPO_EPS' ? 'EPO LIVE' : source.includes('LOCAL') && source.includes('EPO') ? 'LOCAL + EPO' : 'LOCAL'}
            </span>
          </div>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#fff', marginBottom: '8px', lineHeight: 1.4 }}>
            {patent.title}
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
            <span><strong>Applicant:</strong> {applicant}</span>
            <span><strong>Classification:</strong> {classification}</span>
            {patent.field_of_invention && <span><strong>Field:</strong> {patent.field_of_invention}</span>}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
          {/* Hybrid Score (Phase 6A) */}
          {finalPercent !== null && (
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '9px', textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', fontWeight: 600 }}>
                Hybrid Score
              </span>
              <span className={`novelty-status-pill ${getScoreColorClass(finalPercent)}`}>
                {finalPercent}%
              </span>
            </div>
          )}

          {/* Semantic Similarity Score */}
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '9px', textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', fontWeight: 600 }}>
              Semantic
            </span>
            <span className={`novelty-status-pill ${getScoreColorClass(simPercent)}`}>
              {simPercent}%
            </span>
          </div>

          {/* Keyword Score if present */}
          {kwPercent !== null && (
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '9px', textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', fontWeight: 600 }}>
                Keyword
              </span>
              <span className={`novelty-status-pill ${getScoreColorClass(kwPercent)}`}>
                {kwPercent}%
              </span>
            </div>
          )}

          {/* Evidence Score if present in legacy mode */}
          {patent.evidence_score !== undefined && (
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '9px', textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', fontWeight: 600 }}>
                Evidence
              </span>
              <span className={`novelty-status-pill ${getScoreColorClass(patent.evidence_score)}`}>
                {Math.round(patent.evidence_score)}%
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Explainable Ranking Reasons (Phase 6A) */}
      {patent.ranking_reasons && patent.ranking_reasons.length > 0 && (
        <div style={{ marginTop: '12px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {patent.ranking_reasons.map((reason, rIdx) => (
            <span
              key={rIdx}
              style={{
                fontSize: '11px',
                padding: '2px 8px',
                borderRadius: '4px',
                background: 'rgba(59, 130, 246, 0.12)',
                color: '#93c5fd',
                border: '1px solid rgba(59, 130, 246, 0.25)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <span style={{ color: '#38bdf8' }}>✓</span> {reason}
            </span>
          ))}
        </div>
      )}

      {/* Scoring breakdown if available */}
      {patent.scoring_breakdown && (
        <div style={{ 
          marginTop: '12px', 
          padding: '8px 12px', 
          background: 'var(--bg-surface-secondary)', 
          borderRadius: 'var(--border-radius-sm)',
          fontSize: '11px',
          color: 'var(--text-secondary)',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))',
          gap: '8px',
          border: '1px solid var(--border-neutral)'
        }}>
          <div>Semantic Weight: <strong>{patent.scoring_breakdown.semantic}%</strong></div>
          <div>Concept Match: <strong>{patent.scoring_breakdown.concept_coverage}%</strong></div>
          <div>Domain Match: <strong>{patent.scoring_breakdown.domain_alignment}%</strong></div>
          <div>Metadata Match: <strong>{patent.scoring_breakdown.metadata_relevance}%</strong></div>
        </div>
      )}

      {/* Expanded Text Section */}
      {expanded ? (
        <div style={{ 
          marginTop: '16px', 
          paddingTop: '16px', 
          borderTop: '1px solid var(--border-neutral)',
          fontSize: '13px',
          color: 'var(--text-secondary)',
          lineHeight: '1.6',
          whiteSpace: 'pre-line'
        }}>
          <strong>Patent Abstract / Description:</strong>
          <p style={{ marginTop: '8px' }}>{patent.abstract || patent.patent_text}</p>
        </div>
      ) : null}

      <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'flex-end' }}>
        <button 
          className="btn-secondary" 
          onClick={() => setExpanded(!expanded)}
          style={{ padding: '6px 12px', fontSize: '12px', height: 'auto' }}
        >
          {expanded ? 'Collapse Details' : 'View Patent Details'}
        </button>
      </div>
    </div>
  );
}
