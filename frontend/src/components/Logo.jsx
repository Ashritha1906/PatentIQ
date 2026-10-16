import React from 'react';

export function LogoIcon({ size = 32, className = '' }) {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 40 40" 
      width={size} 
      height={size} 
      fill="none"
      className={className}
      style={{ flexShrink: 0, display: 'inline-block', verticalAlign: 'middle' }}
      aria-label="PatentIQ Logo"
    >
      <defs>
        {/* Container Background */}
        <linearGradient id="piqBaseBg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#0B132B"/>
          <stop offset="100%" stopColor="#131D35"/>
        </linearGradient>

        {/* Base Frame Border */}
        <linearGradient id="piqBaseBorder" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.45"/>
          <stop offset="50%" stopColor="#818CF8" stopOpacity="0.25"/>
          <stop offset="100%" stopColor="#34D399" stopOpacity="0.45"/>
        </linearGradient>

        {/* Patent Document Sheet Fill */}
        <linearGradient id="patentDocFill" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#1E293B"/>
          <stop offset="100%" stopColor="#0F172A"/>
        </linearGradient>

        {/* Search Lens Rim Gradient */}
        <linearGradient id="lensRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#60A5FA"/>
          <stop offset="50%" stopColor="#818CF8"/>
          <stop offset="100%" stopColor="#34D399"/>
        </linearGradient>

        {/* AI Spark Glow Filter */}
        <filter id="aiSparkGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="1.5" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {/* 1. Precision Squircle Frame */}
      <rect 
        x="1.5" 
        y="1.5" 
        width="37" 
        height="37" 
        rx="9.5" 
        fill="url(#piqBaseBg)" 
        stroke="url(#piqBaseBorder)" 
        strokeWidth="1.2"
      />

      {/* 2. Patent Document (With Folded Top-Right Corner) */}
      <path 
        d="M9.5 8 A2.5 2.5 0 0 1 12 5.5 H23.5 L30.5 12.5 V31.5 A2.5 2.5 0 0 1 28 34 H12 A2.5 2.5 0 0 1 9.5 31.5 Z" 
        fill="url(#patentDocFill)" 
        stroke="#38BDF8" 
        strokeOpacity="0.45" 
        strokeWidth="1.2"
      />

      {/* 3. Folded Corner Sheet Flap */}
      <path 
        d="M23.5 5.5 V11.5 A1 1 0 0 0 24.5 12.5 H30.5" 
        fill="#1E293B" 
        stroke="#38BDF8" 
        strokeOpacity="0.5" 
        strokeWidth="1.2"
      />

      {/* 4. Patent Claims & Technical Specification Lines */}
      <line x1="13.5" y1="10.5" x2="20" y2="10.5" stroke="#94A3B8" strokeOpacity="0.5" strokeWidth="1.3" strokeLinecap="round"/>
      <line x1="13.5" y1="14.5" x2="25" y2="14.5" stroke="#94A3B8" strokeOpacity="0.4" strokeWidth="1.3" strokeLinecap="round"/>
      <line x1="13.5" y1="18.5" x2="19" y2="18.5" stroke="#94A3B8" strokeOpacity="0.3" strokeWidth="1.3" strokeLinecap="round"/>

      {/* 5. AI Prior-Art Discovery Lens (Scanning the Claims) */}
      <circle 
        cx="21.5" 
        cy="23.5" 
        r="6.8" 
        fill="#0B132B" 
        stroke="url(#lensRingGrad)" 
        strokeWidth="1.8"
      />

      {/* 6. AI Novelty Spark at Lens Focal Point */}
      <path 
        d="M21.5 19 Q21.5 23.5 26 23.5 Q21.5 23.5 21.5 28 Q21.5 23.5 17 23.5 Q21.5 23.5 21.5 19 Z" 
        fill="#34D399" 
        filter="url(#aiSparkGlow)"
      />
      <circle cx="21.5" cy="23.5" r="1.1" fill="#FFFFFF"/>
    </svg>
  );
}

export default function Logo({ 
  size = 32, 
  showWordmark = true, 
  tagline = null, 
  onClick = null,
  className = '' 
}) {
  return (
    <div 
      onClick={onClick}
      className={`patentiq-logo ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: size >= 32 ? '10px' : '8px',
        cursor: onClick ? 'pointer' : 'default',
        userSelect: 'none'
      }}
    >
      <LogoIcon size={size} />

      {showWordmark && (
        <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
            <span style={{ 
              fontSize: size >= 32 ? '18px' : '15px', 
              fontWeight: 800, 
              color: 'var(--text-primary)', 
              letterSpacing: '-0.03em',
              fontFamily: 'var(--font-heading)'
            }}>
              Patent<span style={{
                background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent-violet) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>IQ</span>
            </span>

            {tagline && (
              <span style={{ 
                fontSize: size >= 32 ? '10px' : '9px', 
                fontWeight: 700, 
                color: 'var(--primary)', 
                letterSpacing: '0.06em', 
                textTransform: 'uppercase',
                background: 'var(--primary-glow)',
                padding: '2px 6px',
                borderRadius: '4px',
                border: '1px solid rgba(117, 167, 255, 0.25)'
              }}>
                {tagline}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
