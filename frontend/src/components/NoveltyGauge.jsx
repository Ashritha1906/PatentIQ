import React, { useEffect, useState } from 'react';

export default function NoveltyGauge({ score }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    // Trigger transition animation on mount/update
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  // Determine status color based on score
  const getStatusColor = (val) => {
    if (val >= 70) return 'var(--success)';
    if (val >= 40) return 'var(--warning)';
    return 'var(--error)';
  };

  const activeColor = getStatusColor(score);
  
  // Math for the gauge arc
  // Radius = 70, center is (90, 90)
  // Arc length = Math.PI * 70 = 219.9
  const radius = 70;
  const strokeLength = Math.PI * radius;
  const strokeOffset = strokeLength - (animatedScore / 100) * strokeLength;
  
  // Angle for the needle:
  // Starts at -90 degrees (pointing left) and sweeps 180 degrees to +90 degrees (pointing right)
  const angle = -90 + (animatedScore / 100) * 180;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
      <svg width="180" height="110" viewBox="0 0 180 110" style={{ overflow: 'visible' }}>
        {/* Background Track Arc */}
        <path
          d="M 20 90 A 70 70 0 0 1 160 90"
          fill="none"
          stroke="var(--bg-surface-secondary)"
          strokeWidth="10"
          strokeLinecap="round"
        />
        
        {/* Active Arc Fill */}
        <path
          d="M 20 90 A 70 70 0 0 1 160 90"
          fill="none"
          stroke={activeColor}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={strokeLength}
          strokeDashoffset={strokeOffset}
          style={{
            transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.5s ease',
          }}
        />

        {/* Center Pivot Point */}
        <circle cx="90" cy="90" r="6" fill="#fff" />
        <circle cx="90" cy="90" r="3" fill="var(--bg-base)" />

        {/* Pointer Needle */}
        <g transform={`rotate(${angle}, 90, 90)`} style={{ transition: 'transform 1.2s cubic-bezier(0.4, 0, 0.2, 1)' }}>
          <line
            x1="90"
            y1="90"
            x2="90"
            y2="30"
            stroke="#fff"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <polygon
            points="87,90 93,90 90,25"
            fill="#fff"
          />
        </g>
        
        {/* Label markers */}
        <text x="18" y="105" fill="var(--text-muted)" fontSize="10" textAnchor="middle">0%</text>
        <text x="90" y="15" fill="var(--text-muted)" fontSize="10" textAnchor="middle">50%</text>
        <text x="162" y="105" fill="var(--text-muted)" fontSize="10" textAnchor="middle">100%</text>
      </svg>
    </div>
  );
}
