import React, { useEffect, useState } from 'react';

export default function NoveltyGauge({ score }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  const getStatusColor = (val) => {
    if (val >= 70) return 'var(--success)';
    if (val >= 40) return 'var(--warning)';
    return 'var(--error)';
  };

  const activeColor = getStatusColor(score);
  const radius = 68;
  const strokeLength = Math.PI * radius;
  const strokeOffset = strokeLength - (animatedScore / 100) * strokeLength;
  const angle = -90 + (animatedScore / 100) * 180;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <svg width="180" height="105" viewBox="0 0 180 105" style={{ overflow: 'visible' }}>
        {/* Background Track Arc */}
        <path
          d="M 22 90 A 68 68 0 0 1 158 90"
          fill="none"
          stroke="var(--border-neutral)"
          strokeWidth="8"
          strokeLinecap="round"
        />
        
        {/* Active Arc Fill */}
        <path
          d="M 22 90 A 68 68 0 0 1 158 90"
          fill="none"
          stroke={activeColor}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={strokeLength}
          strokeDashoffset={strokeOffset}
          style={{
            transition: 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease',
          }}
        />

        {/* Center Pivot Point */}
        <circle cx="90" cy="90" r="5" fill="var(--text-primary)" />
        <circle cx="90" cy="90" r="2.5" fill="var(--bg-surface)" />

        {/* Pointer Needle */}
        <g transform={`rotate(${angle}, 90, 90)`} style={{ transition: 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)' }}>
          <line
            x1="90"
            y1="90"
            x2="90"
            y2="32"
            stroke="var(--text-primary)"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
        </g>
        
        {/* Label Markers */}
        <text x="20" y="103" fill="var(--text-muted)" fontSize="9" fontWeight="600" textAnchor="middle">0%</text>
        <text x="90" y="14" fill="var(--text-muted)" fontSize="9" fontWeight="600" textAnchor="middle">50%</text>
        <text x="160" y="103" fill="var(--text-muted)" fontSize="9" fontWeight="600" textAnchor="middle">100%</text>
      </svg>
      <div style={{ textAlign: 'center', marginTop: '-12px' }}>
        <span style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>
          {score}%
        </span>
        <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', letterSpacing: '0.04em' }}>
          Estimated Novelty
        </span>
      </div>
    </div>
  );
}
