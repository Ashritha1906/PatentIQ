import React, { useState, useRef } from 'react';
import { Icon } from './Icons';

export function HeroVisualization({ onNavigate }) {
  const [activeNode, setActiveNode] = useState(0);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const containerRef = useRef(null);

  const patentNodes = [
    {
      id: 0,
      pubId: 'EP3892014A1',
      title: 'Automated Thermal Satellite Imagery Analysis',
      applicant: 'European Aerospace Labs',
      registry: 'EPO Live Registry',
      similarity: 91,
      ipc: 'G06T 7/00 &bull; B64G 1/10',
      sharedMechanism: 'Multi-band infrared thermal thresholding with spectral false-positive filtering.',
      divergence: 'Operates on low-resolution GEO satellite telemetry rather than edge drone vision.',
      status: 'high'
    },
    {
      id: 1,
      pubId: 'IN202341088921A',
      title: 'Multi-Sensor Aerial Smoke Trajectory Prediction',
      applicant: 'National Institute of Space Tech',
      registry: 'Indian Patent Office',
      similarity: 84,
      ipc: 'G08B 17/12 &bull; G01N 21/35',
      sharedMechanism: 'Temporal vector tracking of smoke plume vectors using Kalman motion estimates.',
      divergence: 'Lacks real-time autonomous path re-planning for onboard collision avoidance.',
      status: 'medium'
    },
    {
      id: 2,
      pubId: 'EP3451290B1',
      title: 'Constellation Deep Learning Hazard Tracking',
      applicant: 'Orbital Dynamics SE',
      registry: 'EPO Live Registry',
      similarity: 78,
      ipc: 'H04B 7/185 &bull; G06N 3/08',
      sharedMechanism: 'Constellation downlink aggregation with multi-angle stereoscopic modeling.',
      divergence: 'Relies entirely on cloud ground-stations; 15-minute telemetry latency.',
      status: 'medium'
    },
    {
      id: 3,
      pubId: 'IN202211045210A',
      title: 'Early-Stage Forest Fire Infrared Detection',
      applicant: 'Forestry Robotics Consortium',
      registry: 'Indian Patent Office',
      similarity: 72,
      ipc: 'B64U 10/14 &bull; A62C 3/02',
      sharedMechanism: 'Lightweight UAV infrared pod with fixed downward-looking optics.',
      divergence: 'Does not integrate satellite telemetry constellation feed or SLAM state.',
      status: 'low'
    }
  ];

  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    // Restrained, subtle 3D tilt
    setTilt({
      x: -(y / rect.height) * 8,
      y: (x / rect.width) * 8
    });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  const activeData = patentNodes[activeNode];

  return (
    <div 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="hero-vis-container"
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '920px',
        margin: '0 auto',
        transform: `perspective(1000px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
        transition: 'transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        willChange: 'transform'
      }}
    >
      {/* 1. VISUALIZATION CANVAS CARD */}
      <div 
        className="panel"
        style={{
          position: 'relative',
          background: 'linear-gradient(145deg, var(--bg-surface) 0%, var(--bg-surface-secondary) 100%)',
          border: '1px solid var(--border-neutral)',
          borderRadius: 'var(--border-radius-xl)',
          padding: '24px 24px 28px 24px',
          boxShadow: '0 24px 48px -12px rgba(0, 0, 0, 0.45), 0 0 32px var(--primary-glow)',
          overflow: 'hidden'
        }}
      >
        {/* Top Header Console Bar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)', boxShadow: '0 0 8px var(--primary)' }}></span>
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
              Semantic Prior-Art Relationship Topology
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge-provenance combined" style={{ fontSize: '11px', padding: '3px 9px' }}>
              4 Nodes Linked
            </span>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              Dense 384-D Vector Space
            </span>
          </div>
        </div>

        {/* 2. THE SVG RELATIONSHIP TOPOLOGY GRAPH */}
        <div style={{ position: 'relative', height: '340px', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          
          {/* Background Animated SVG Bezier Connectors */}
          <svg 
            width="100%" 
            height="100%" 
            viewBox="0 0 800 340" 
            style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none', overflow: 'visible' }}
          >
            <defs>
              <linearGradient id="glowLineActive" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.8" />
                <stop offset="100%" stopColor="var(--accent-violet)" stopOpacity="0.9" />
              </linearGradient>
              <linearGradient id="glowLineInactive" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="var(--border-neutral)" stopOpacity="0.4" />
                <stop offset="100%" stopColor="var(--border-neutral)" stopOpacity="0.2" />
              </linearGradient>
            </defs>

            {/* Bezier curves from Center (400, 170) to 4 Nodes */}
            {/* Top-Right Node: ~ (640, 65) */}
            <path 
              d="M 400 170 C 480 170, 560 65, 640 65" 
              fill="none" 
              stroke={activeNode === 0 ? "url(#glowLineActive)" : "url(#glowLineInactive)"} 
              strokeWidth={activeNode === 0 ? "2.5" : "1.5"} 
              strokeDasharray={activeNode === 0 ? "6 4" : "4 4"}
              className={activeNode === 0 ? "path-active-pulse" : ""}
            />

            {/* Bottom-Right Node: ~ (640, 275) */}
            <path 
              d="M 400 170 C 480 170, 560 275, 640 275" 
              fill="none" 
              stroke={activeNode === 1 ? "url(#glowLineActive)" : "url(#glowLineInactive)"} 
              strokeWidth={activeNode === 1 ? "2.5" : "1.5"} 
              strokeDasharray={activeNode === 1 ? "6 4" : "4 4"}
              className={activeNode === 1 ? "path-active-pulse" : ""}
            />

            {/* Bottom-Left Node: ~ (160, 275) */}
            <path 
              d="M 400 170 C 320 170, 240 275, 160 275" 
              fill="none" 
              stroke={activeNode === 2 ? "url(#glowLineActive)" : "url(#glowLineInactive)"} 
              strokeWidth={activeNode === 2 ? "2.5" : "1.5"} 
              strokeDasharray={activeNode === 2 ? "6 4" : "4 4"}
              className={activeNode === 2 ? "path-active-pulse" : ""}
            />

            {/* Top-Left Node: ~ (160, 65) */}
            <path 
              d="M 400 170 C 320 170, 240 65, 160 65" 
              fill="none" 
              stroke={activeNode === 3 ? "url(#glowLineActive)" : "url(#glowLineInactive)"} 
              strokeWidth={activeNode === 3 ? "2.5" : "1.5"} 
              strokeDasharray={activeNode === 3 ? "6 4" : "4 4"}
              className={activeNode === 3 ? "path-active-pulse" : ""}
            />

            {/* Concentric Center Radar Rings */}
            <circle cx="400" cy="170" r="70" fill="none" stroke="var(--primary)" strokeOpacity="0.08" strokeWidth="1" />
            <circle cx="400" cy="170" r="110" fill="none" stroke="var(--primary)" strokeOpacity="0.05" strokeWidth="1" strokeDasharray="3 6" />
          </svg>

          {/* CENTRAL INVENTION NODE (The Anchor) */}
          <div 
            style={{
              position: 'relative',
              zIndex: 10,
              background: 'linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-surface-elevated) 100%)',
              border: '2px solid var(--primary)',
              boxShadow: '0 0 24px var(--primary-glow), 0 8px 16px rgba(0,0,0,0.3)',
              borderRadius: 'var(--border-radius-lg)',
              padding: '14px 18px',
              textAlign: 'center',
              width: '240px'
            }}
          >
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'var(--primary-glow)', padding: '2px 8px', borderRadius: '4px', marginBottom: '6px' }}>
              <Icon name="sparkles" size={13} color="var(--primary)" />
              <span style={{ fontSize: '10.5px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase' }}>
                Your Research Idea
              </span>
            </div>
            
            <h4 style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 4px 0', lineHeight: 1.3 }}>
              Multi-Spectral Wildfire Detection & Satellite SLAM
            </h4>
            
            <span style={{ fontSize: '10.5px', color: 'var(--text-muted)' }}>
              Semantic Query Vector &bull; 384-D
            </span>
          </div>

          {/* 4 ORBITING PATENT DOCUMENT NODES (Interactive Buttons) */}
          
          {/* Node 0: Top-Right */}
          <div 
            onClick={() => setActiveNode(0)}
            style={{
              position: 'absolute',
              top: '18px',
              right: '20px',
              zIndex: 5,
              cursor: 'pointer',
              background: activeNode === 0 ? 'var(--bg-surface-elevated)' : 'var(--bg-surface)',
              border: activeNode === 0 ? '1.5px solid var(--primary)' : '1px solid var(--border-neutral)',
              boxShadow: activeNode === 0 ? '0 8px 20px -4px var(--primary-glow)' : 'var(--shadow-sm)',
              borderRadius: 'var(--border-radius-md)',
              padding: '10px 14px',
              width: '210px',
              transition: 'all var(--transition-fast)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
              <span className="font-mono" style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)' }}>
                EP3892014A1
              </span>
              <span style={{ fontSize: '10.5px', fontWeight: 700, color: 'var(--success)', background: 'var(--success-glow)', padding: '1px 6px', borderRadius: '3px' }}>
                91% Match
              </span>
            </div>
            <div style={{ fontSize: '11.5px', fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              Automated Thermal Satellite Imagery
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
              EPO Live &bull; G06T 7/00
            </div>
          </div>

          {/* Node 1: Bottom-Right */}
          <div 
            onClick={() => setActiveNode(1)}
            style={{
              position: 'absolute',
              bottom: '18px',
              right: '20px',
              zIndex: 5,
              cursor: 'pointer',
              background: activeNode === 1 ? 'var(--bg-surface-elevated)' : 'var(--bg-surface)',
              border: activeNode === 1 ? '1.5px solid var(--primary)' : '1px solid var(--border-neutral)',
              boxShadow: activeNode === 1 ? '0 8px 20px -4px var(--primary-glow)' : 'var(--shadow-sm)',
              borderRadius: 'var(--border-radius-md)',
              padding: '10px 14px',
              width: '210px',
              transition: 'all var(--transition-fast)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
              <span className="font-mono" style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-violet)' }}>
                IN202341088921A
              </span>
              <span style={{ fontSize: '10.5px', fontWeight: 700, color: 'var(--primary)', background: 'var(--primary-glow)', padding: '1px 6px', borderRadius: '3px' }}>
                84% Match
              </span>
            </div>
            <div style={{ fontSize: '11.5px', fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              Aerial Smoke Trajectory Prediction
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Indian Patent &bull; G08B 17/12
            </div>
          </div>

          {/* Node 2: Bottom-Left */}
          <div 
            onClick={() => setActiveNode(2)}
            style={{
              position: 'absolute',
              bottom: '18px',
              left: '20px',
              zIndex: 5,
              cursor: 'pointer',
              background: activeNode === 2 ? 'var(--bg-surface-elevated)' : 'var(--bg-surface)',
              border: activeNode === 2 ? '1.5px solid var(--primary)' : '1px solid var(--border-neutral)',
              boxShadow: activeNode === 2 ? '0 8px 20px -4px var(--primary-glow)' : 'var(--shadow-sm)',
              borderRadius: 'var(--border-radius-md)',
              padding: '10px 14px',
              width: '210px',
              transition: 'all var(--transition-fast)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
              <span className="font-mono" style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)' }}>
                EP3451290B1
              </span>
              <span style={{ fontSize: '10.5px', fontWeight: 700, color: 'var(--text-secondary)', background: 'var(--bg-surface-secondary)', padding: '1px 6px', borderRadius: '3px' }}>
                78% Match
              </span>
            </div>
            <div style={{ fontSize: '11.5px', fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              Constellation Hazard Tracking
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
              EPO Live &bull; H04B 7/185
            </div>
          </div>

          {/* Node 3: Top-Left */}
          <div 
            onClick={() => setActiveNode(3)}
            style={{
              position: 'absolute',
              top: '18px',
              left: '20px',
              zIndex: 5,
              cursor: 'pointer',
              background: activeNode === 3 ? 'var(--bg-surface-elevated)' : 'var(--bg-surface)',
              border: activeNode === 3 ? '1.5px solid var(--primary)' : '1px solid var(--border-neutral)',
              boxShadow: activeNode === 3 ? '0 8px 20px -4px var(--primary-glow)' : 'var(--shadow-sm)',
              borderRadius: 'var(--border-radius-md)',
              padding: '10px 14px',
              width: '210px',
              transition: 'all var(--transition-fast)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
              <span className="font-mono" style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-violet)' }}>
                IN202211045210A
              </span>
              <span style={{ fontSize: '10.5px', fontWeight: 700, color: 'var(--text-secondary)', background: 'var(--bg-surface-secondary)', padding: '1px 6px', borderRadius: '3px' }}>
                72% Match
              </span>
            </div>
            <div style={{ fontSize: '11.5px', fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              Forest Fire Infrared Detection
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Indian Patent &bull; B64U 10/14
            </div>
          </div>

        </div>

        {/* 3. DYNAMIC EVIDENCE PANEL (Interactive Context for the Selected Node) */}
        <div 
          style={{
            marginTop: '16px',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-neutral)',
            borderRadius: 'var(--border-radius-md)',
            padding: '16px 20px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '16px',
            alignItems: 'center'
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase' }}>
                Active Prior Art Evidence:
              </span>
              <span className="font-mono" style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)' }}>
                {activeData.pubId}
              </span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                ({activeData.registry})
              </span>
            </div>
            
            <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              <strong style={{ color: 'var(--success)' }}>Overlapping Mechanism:</strong> {activeData.sharedMechanism}
            </div>
          </div>

          <div style={{ borderLeft: '1px solid var(--border-neutral)', paddingLeft: '16px' }}>
            <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '10px' }}>
              <strong style={{ color: 'var(--accent-violet)' }}>Technical Differentiation:</strong> {activeData.divergence}
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                onClick={() => onNavigate('compare')}
                className="btn-secondary"
                style={{ padding: '4px 10px', fontSize: '11.5px', fontWeight: 600 }}
              >
                <span>Compare Claims in Matrix</span>
                <Icon name="arrow-right" size={12} />
              </button>
              <button 
                onClick={() => onNavigate('copilot')}
                className="btn-ghost"
                style={{ padding: '4px 10px', fontSize: '11.5px', color: 'var(--primary)' }}
              >
                <Icon name="copilot" size={12} />
                <span>Ask Copilot</span>
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default HeroVisualization;
