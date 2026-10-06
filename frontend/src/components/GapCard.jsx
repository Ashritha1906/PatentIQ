import React from 'react';

export default function GapCard({ gap }) {
  const status = gap.representation_status || gap.coverage_band || 'Weakly Represented';
  const conceptName = gap.concept || gap.opportunity || 'Technical Parameter';
  const isCombination = gap.is_combination || false;
  const coverageScore = gap.coverage_score !== undefined ? Math.round(gap.coverage_score) : null;
  const equivalents = gap.matched_equivalents || [];

  const getBadgeStyle = (statusVal) => {
    switch ((statusVal || '').toLowerCase()) {
      case 'missing':
      case 'no meaningful evidence':
        return { backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--error)' };
      case 'weakly represented':
      case 'minimally represented':
      case 'weak':
        return { backgroundColor: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' };
      case 'moderately represented':
        return { backgroundColor: 'rgba(59, 130, 246, 0.1)', color: '#60a5fa' };
      default:
        return { backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' };
    }
  };

  const badgeStyle = getBadgeStyle(status);

  return (
    <div 
      className="panel panel-padding" 
      style={{ 
        background: 'var(--bg-surface)', 
        border: isCombination ? '1px solid rgba(139, 92, 246, 0.4)' : '1px solid var(--border-neutral)',
        borderRadius: 'var(--border-radius-lg)',
        marginBottom: '16px',
        boxShadow: isCombination ? '0 0 12px rgba(139, 92, 246, 0.08)' : 'none'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', margin: 0 }}>
            {conceptName}
          </h4>
          {isCombination && (
            <span style={{ fontSize: '10px', background: 'rgba(139, 92, 246, 0.15)', color: '#c084fc', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>
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
              fontSize: '11px', 
              fontWeight: 600, 
              padding: '2px 10px', 
              borderRadius: '50px',
              textTransform: 'uppercase',
              letterSpacing: '0.02em',
              ...badgeStyle
            }}
          >
            {status}
          </span>
        </div>
      </div>
      
      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', margin: '0 0 10px 0' }}>
        {gap.explanation}
      </p>

      {/* Semantic equivalents chips if found */}
      {equivalents.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', marginTop: '8px', fontSize: '11px' }}>
          <span style={{ color: 'var(--text-muted)' }}>Semantic matches:</span>
          {equivalents.slice(0, 4).map((eq, i) => (
            <span key={i} style={{ background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)', padding: '1px 6px', borderRadius: '4px', color: 'var(--primary-light)' }}>
              {eq}
            </span>
          ))}
        </div>
      )}

      {gap.containing_patents && gap.containing_patents.length > 0 && (
        <div style={{ marginTop: '10px', fontSize: '11px', color: 'var(--text-muted)' }}>
          Prior Art Alignment: {gap.containing_patents.slice(0, 6).join(', ')}
        </div>
      )}
    </div>
  );
}
