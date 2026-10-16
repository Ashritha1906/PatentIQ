import React from 'react';

export default function GapCard({ gap }) {
  const status = gap.representation_status || gap.coverage_band || 'Weakly Represented';
  const conceptName = gap.concept || gap.opportunity || 'Technical Parameter';
  const isCombination = gap.is_combination || false;
  const coverageScore = gap.coverage_score !== undefined ? Math.round(gap.coverage_score) : null;
  const equivalents = gap.matched_equivalents || [];

  const getStatusBadge = (statusVal) => {
    switch ((statusVal || '').toLowerCase()) {
      case 'missing':
      case 'no meaningful evidence':
      case 'minimal':
      case 'minimally represented':
        return { bg: 'rgba(239, 68, 68, 0.1)', color: 'var(--error)', border: 'rgba(239, 68, 68, 0.25)' };
      case 'weak':
      case 'weakly represented':
        return { bg: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)', border: 'rgba(245, 158, 11, 0.25)' };
      case 'moderate':
      case 'moderately represented':
        return { bg: 'rgba(110, 168, 254, 0.1)', color: 'var(--primary)', border: 'rgba(110, 168, 254, 0.25)' };
      default:
        return { bg: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)', border: 'rgba(16, 185, 129, 0.25)' };
    }
  };

  const badgeStyle = getStatusBadge(status);

  return (
    <div 
      className="panel panel-padding" 
      style={{ 
        background: 'var(--bg-surface)', 
        border: isCombination ? '1px solid rgba(155, 138, 251, 0.35)' : '1px solid var(--border-neutral)',
        marginBottom: '12px',
        boxShadow: isCombination ? '0 0 16px rgba(155, 138, 251, 0.05)' : 'none'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <h4 style={{ fontSize: '14.5px', fontWeight: 600, color: '#fff', margin: 0 }}>
            {conceptName}
          </h4>
          {isCombination && (
            <span style={{ fontSize: '10px', background: 'rgba(155, 138, 251, 0.15)', color: 'var(--accent-violet-light)', border: '1px solid rgba(155, 138, 251, 0.3)', padding: '1px 6px', borderRadius: '4px', fontWeight: 600 }}>
              COMBINATION GAP
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {coverageScore !== null && (
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 500 }}>
              Coverage: {coverageScore}%
            </span>
          )}
          <span 
            style={{ 
              fontSize: '10.5px', 
              fontWeight: 600, 
              padding: '2px 8px', 
              borderRadius: '4px',
              textTransform: 'uppercase',
              letterSpacing: '0.02em',
              background: badgeStyle.bg,
              color: badgeStyle.color,
              border: `1px solid ${badgeStyle.border}`
            }}
          >
            {status}
          </span>
        </div>
      </div>
      
      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55, margin: '0 0 8px 0' }}>
        {gap.explanation}
      </p>

      {/* Semantic equivalents */}
      {equivalents.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', marginTop: '6px', fontSize: '11px' }}>
          <span style={{ color: 'var(--text-muted)' }}>Semantic matches:</span>
          {equivalents.slice(0, 4).map((eq, i) => (
            <span key={i} style={{ background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)', padding: '1px 6px', borderRadius: '4px', color: 'var(--primary)' }}>
              {eq}
            </span>
          ))}
        </div>
      )}

      {gap.containing_patents && gap.containing_patents.length > 0 && (
        <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
          Prior Art Alignment: {gap.containing_patents.slice(0, 6).join(', ')}
        </div>
      )}
    </div>
  );
}
