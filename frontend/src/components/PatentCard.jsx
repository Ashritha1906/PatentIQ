import React, { useState } from 'react';
import { Icon } from './Icons';

/**
 * PatentCard Component
 * Displays a single patent retrieval match with full explainability details,
 * metadata provenance badges, selection checkbox for comparison, and Deep-Dive exploration.
 */
export default function PatentCard({ 
  patent, 
  highlightClass = '',
  selectable = false,
  selected = false,
  onToggleSelect = null,
  onDeepDive = null
}) {
  const [expanded, setExpanded] = useState(false);

  if (!patent) return null;

  const appNum = patent.application_number || patent.publication_number || 'Unknown ID';
  
  // Extract publication date or application year
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
  const source = patent.source || 'LOCAL_PATENTIQ';

  const simPercent = Math.round((patent.semantic_score ?? patent.similarity_score ?? 0) * 100);
  const kwPercent = patent.keyword_score !== undefined ? Math.round(patent.keyword_score * 100) : null;
  const finalPercent = patent.final_score !== undefined ? Math.round(patent.final_score * 100) : null;

  const getSourceBadge = () => {
    if (source.includes('EPO') && source.includes('LOCAL')) {
      return { label: 'LOCAL + EPO', className: 'badge-source-fused' };
    }
    if (source === 'EPO_EPS' || source.includes('EPO')) {
      return { label: 'EPO LIVE', className: 'badge-source-epo' };
    }
    return { label: 'LOCAL PATENTIQ', className: 'badge-source-local' };
  };

  const sourceBadge = getSourceBadge();

  return (
    <div 
      className={`panel interactive panel-padding ${highlightClass}`} 
      id={`patent-${appNum.replace(/[^a-zA-Z0-9]/g, '-')}`}
      style={{
        marginBottom: '14px',
        transition: 'all var(--transition-fast)',
        borderLeft: selected ? '3px solid var(--primary)' : highlightClass ? '3px solid var(--accent-violet)' : '1px solid var(--border-neutral)',
        background: selected ? 'rgba(110, 168, 254, 0.04)' : undefined
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '280px' }}>
          {/* Header Metadata & Tags */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', flexWrap: 'wrap' }}>
            {selectable && (
              <label 
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  cursor: 'pointer',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: selected ? 'var(--primary)' : 'var(--text-muted)',
                  background: selected ? 'var(--primary-glow)' : 'var(--bg-surface-secondary)',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  border: `1px solid ${selected ? 'rgba(110, 168, 254, 0.5)' : 'var(--border-neutral)'}`,
                  userSelect: 'none'
                }}
              >
                <input 
                  type="checkbox"
                  checked={selected}
                  onChange={() => onToggleSelect && onToggleSelect(patent)}
                  style={{ cursor: 'pointer', accentColor: 'var(--primary)' }}
                />
                <span>{selected ? 'Selected for comparison' : 'Compare'}</span>
              </label>
            )}

            <span className="font-mono" style={{ color: 'var(--text-muted)', fontWeight: 600 }}>
              {appNum}
            </span>

            {year && (
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                ({year})
              </span>
            )}

            <span className={`badge ${sourceBadge.className}`}>
              {sourceBadge.label}
            </span>
          </div>

          {/* Patent Title */}
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '8px', lineHeight: 1.4 }}>
            {patent.title}
          </h3>

          {/* Core Metadata */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '14px', fontSize: '12px', color: 'var(--text-secondary)' }}>
            <span><strong style={{ color: 'var(--text-muted)' }}>Applicant:</strong> {applicant}</span>
            <span><strong style={{ color: 'var(--text-muted)' }}>IPC:</strong> {classification}</span>
            {patent.field_of_invention && (
              <span><strong style={{ color: 'var(--text-muted)' }}>Field:</strong> {patent.field_of_invention}</span>
            )}
          </div>
        </div>

        {/* Score Badges */}
        <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
          {finalPercent !== null && (
            <div style={{ textAlign: 'center', background: 'var(--bg-surface-secondary)', padding: '4px 8px', borderRadius: '4px', border: '1px solid var(--border-neutral)' }}>
              <span style={{ fontSize: '9px', textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', fontWeight: 600 }}>
                Hybrid
              </span>
              <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--primary)' }}>
                {finalPercent}%
              </span>
            </div>
          )}

          <div style={{ textAlign: 'center', background: 'var(--bg-surface-secondary)', padding: '4px 8px', borderRadius: '4px', border: '1px solid var(--border-neutral)' }}>
            <span style={{ fontSize: '9px', textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', fontWeight: 600 }}>
              Semantic
            </span>
            <span style={{ fontSize: '13px', fontWeight: 700, color: '#fff' }}>
              {simPercent}%
            </span>
          </div>

          {kwPercent !== null && (
            <div style={{ textAlign: 'center', background: 'var(--bg-surface-secondary)', padding: '4px 8px', borderRadius: '4px', border: '1px solid var(--border-neutral)' }}>
              <span style={{ fontSize: '9px', textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', fontWeight: 600 }}>
                Keyword
              </span>
              <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-secondary)' }}>
                {kwPercent}%
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Explainable Ranking Reasons */}
      {patent.ranking_reasons && patent.ranking_reasons.length > 0 && (
        <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {patent.ranking_reasons.map((reason, rIdx) => (
            <span
              key={rIdx}
              style={{
                fontSize: '11px',
                padding: '2px 8px',
                borderRadius: '4px',
                background: 'rgba(110, 168, 254, 0.08)',
                color: 'var(--primary-light)',
                border: '1px solid rgba(110, 168, 254, 0.2)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <span style={{ color: 'var(--primary)' }}>•</span> {reason}
            </span>
          ))}
        </div>
      )}

      {/* Expanded Abstract Section */}
      {expanded && (
        <div style={{ 
          marginTop: '14px', 
          paddingTop: '14px', 
          borderTop: '1px solid var(--border-neutral)',
          fontSize: '13px',
          color: 'var(--text-secondary)',
          lineHeight: '1.6'
        }}>
          <div style={{ fontWeight: 600, color: '#fff', marginBottom: '6px' }}>Patent Abstract:</div>
          <p style={{ margin: 0 }}>
            {patent.abstract || patent.patent_text || 'No abstract text available in indexed record.'}
          </p>
        </div>
      )}

      {/* Action Footer */}
      <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
        {onDeepDive && (
          <button 
            className="btn-secondary" 
            onClick={() => onDeepDive(patent)}
            style={{ padding: '5px 10px', fontSize: '12px' }}
          >
            <Icon name="search" size={13} color="var(--primary)" />
            Deep Dive
          </button>
        )}
        <button 
          className="btn-secondary" 
          onClick={() => setExpanded(!expanded)}
          style={{ padding: '5px 10px', fontSize: '12px' }}
        >
          {expanded ? 'Hide Details' : 'View Details'}
          <Icon name={expanded ? 'chevron-down' : 'chevron-right'} size={13} />
        </button>
      </div>
    </div>
  );
}
