import React, { useEffect, useRef } from 'react';

// Canvas-based Animated Neural Network background component
function NeuralBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let animationFrameId;

    // Resize handler
    const resizeCanvas = () => {
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight || 450;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particle nodes definition
    const nodeCount = 50;
    const nodes = [];
    
    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1.5
      });
    }

    // Animation Loop
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Update & Draw nodes
      nodes.forEach((node) => {
        node.x += node.vx;
        node.y += node.vy;

        // Boundary checks
        if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
        if (node.y < 0 || node.y > canvas.height) node.vy *= -1;

        // Draw particle node
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(99, 102, 241, 0.25)';
        ctx.fill();
      });

      // Draw connections (lines) between close nodes
      ctx.strokeStyle = 'rgba(99, 102, 241, 0.08)';
      ctx.lineWidth = 0.8;
      
      for (let i = 0; i < nodeCount; i++) {
        for (let j = i + 1; j < nodeCount; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 110) {
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas 
      ref={canvasRef} 
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 1
      }}
    />
  );
}

export default function Home({ onNavigate }) {
  return (
    <div className="container" style={{ position: 'relative' }}>
      {/* Hero Section with Neural Network Canvas */}
      <section 
        className="hero-section" 
        style={{ 
          position: 'relative', 
          overflow: 'hidden', 
          borderRadius: 'var(--border-radius-lg)', 
          background: 'radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.04) 0%, transparent 80%)',
          border: '1px solid var(--border-neutral)',
          padding: '64px 32px',
          margin: '32px auto 48px auto'
        }}
      >
        <NeuralBackground />
        
        <div style={{ position: 'relative', zIndex: 2 }}>
          <span style={{ 
            fontSize: '11px', 
            fontWeight: 700, 
            color: 'var(--primary-light)', 
            textTransform: 'uppercase', 
            letterSpacing: '0.15em',
            display: 'block',
            marginBottom: '12px'
          }}>
            Version 2.0 Released
          </span>
          <h1 className="hero-title" style={{ fontSize: '48px', fontWeight: 700, marginBottom: '20px' }}>
            Transform Ideas into Patent Intelligence
          </h1>
          <p className="hero-subtitle" style={{ fontSize: '16.5px', marginBottom: '36px', maxWidth: '640px' }}>
            Accelerate your technology research loop. Instantly index prior art vectors, map technical spaces, evaluate novelty indices, and draft Gemini RAG comparative reports.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <button 
              className="btn-primary" 
              onClick={() => onNavigate('workspace')}
              style={{ padding: '14px 28px', fontSize: '14.5px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              Launch Research Workspace <span>→</span>
            </button>
            <button 
              className="btn-secondary" 
              onClick={() => onNavigate('docs')}
              style={{ padding: '14px 28px', fontSize: '14.5px', fontWeight: 600 }}
            >
              View API Documentation
            </button>
          </div>
        </div>
      </section>

      {/* Trust Statistics Row */}
      <section className="trust-metrics-row" style={{ margin: '0 auto 64px auto' }}>
        <div>
          <div className="metric-num">115,625+</div>
          <div className="metric-label">Patent Records</div>
        </div>
        <div>
          <div className="metric-num">94.65%</div>
          <div className="metric-label">Intelligence Score</div>
        </div>
        <div>
          <div className="metric-num">0.0%</div>
          <div className="metric-label">Hallucination Rate</div>
        </div>
        <div>
          <div className="metric-num">384-D</div>
          <div className="metric-label">Vector Embeddings</div>
        </div>
      </section>

      {/* Pipeline Progression Layout */}
      <section className="how-it-works-section" style={{ margin: '0 auto 64px auto' }}>
        <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px', color: '#fff' }}>
          Platform AI Analytical Workflow
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '32px' }}>
          Four robust analytical phases executing sequentially to compile structured innovation metrics.
        </p>
        
        <div className="how-it-works-grid">
          <div className="panel process-step-card" style={{ background: 'var(--bg-surface)' }}>
            <div className="step-num">01</div>
            <h3 className="step-title">Query Processing</h3>
            <p className="step-description">Analyzes invention criteria parameters and extracts core technology domains.</p>
          </div>
          <div className="panel process-step-card" style={{ background: 'var(--bg-surface)' }}>
            <div className="step-num">02</div>
            <h3 className="step-title">Vector Search</h3>
            <p className="step-description">Computes semantic proximity weights inside the local ChromaDB index.</p>
          </div>
          <div className="panel process-step-card" style={{ background: 'var(--bg-surface)' }}>
            <div className="step-num">03</div>
            <h3 className="step-title">Landscape Mapping</h3>
            <p className="step-description">Calculates novelty percentages and checks concept overlap whitespace coverage.</p>
          </div>
          <div className="panel process-step-card" style={{ background: 'var(--bg-surface)' }}>
            <div className="step-num">04</div>
            <h3 className="step-title">Generative Summary</h3>
            <p className="step-description">Synthesizes a comparative executive dashboard report using Gemini RAG.</p>
          </div>
        </div>
      </section>

      {/* Feature capabilities */}
      <section className="features-section" style={{ margin: '0 auto 64px auto' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '24px', color: '#fff', textAlign: 'center' }}>
          Enterprise-Grade Intelligence Features
        </h2>
        <div className="features-grid">
          <div className="panel feature-card" style={{ background: 'var(--bg-surface)' }}>
            <div className="feature-icon-box">🔍</div>
            <div>
              <h3 className="feature-title">Semantic Proximity</h3>
              <p className="feature-description">
                Performs multi-dimensional concept searches that match meaning and classifications over simple keywords.
              </p>
            </div>
          </div>
          <div className="panel feature-card" style={{ background: 'var(--bg-surface)' }}>
            <div className="feature-icon-box">📊</div>
            <div>
              <h3 className="feature-title">Novelty Assessment</h3>
              <p className="feature-description">
                Provides a weighted novelty index by cross-referencing similarity overlaps and key parameters coverage.
              </p>
            </div>
          </div>
          <div className="panel feature-card" style={{ background: 'var(--bg-surface)' }}>
            <div className="feature-icon-box">💡</div>
            <div>
              <h3 className="feature-title">Whitespace Gap Spotter</h3>
              <p className="feature-description">
                Identifies missing or weakly represented technology components to point out open innovation pathways.
              </p>
            </div>
          </div>
          <div className="panel feature-card" style={{ background: 'var(--bg-surface)' }}>
            <div className="feature-icon-box">🕸️</div>
            <div>
              <h3 className="feature-title">Patent Graphs</h3>
              <p className="feature-description">
                Draws interactive vector cluster graphs linking your ideas to overlapping patent documents.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Placeholders */}
      <section style={{ margin: '0 auto 80px auto' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '24px', color: '#fff', textAlign: 'center' }}>
          Trusted by Research Teams
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', fontStyle: 'italic', lineHeight: '1.6', marginBottom: '16px' }}>
              "PatentIQ has accelerated our initial freedom-to-operate checks by days. The semantic search queries locate matches that standard keyword filters regularly missed."
            </p>
            <strong style={{ fontSize: '13px', color: '#fff', display: 'block' }}>Dr. Elena Rostova</strong>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Lead AI Researcher, BioTech Solutions</span>
          </div>

          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', fontStyle: 'italic', lineHeight: '1.6', marginBottom: '16px' }}>
              "The whitespace gap detection is extremely valuable. It immediately points out where the saturation limits are, letting our engineers focus on open innovation spaces."
            </p>
            <strong style={{ fontSize: '13px', color: '#fff', display: 'block' }}>Marcus Vance</strong>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>VP of Product, GridLogic Energy</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border-neutral)', padding: '32px 0 64px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          © {new Date().getFullYear()} PatentIQ Inc. All rights reserved.
        </div>
        <div style={{ display: 'flex', gap: '20px', fontSize: '13px' }}>
          <a href="#workspace" onClick={(e) => { e.preventDefault(); onNavigate('workspace'); }}>Workspace</a>
          <a href="#docs" onClick={(e) => { e.preventDefault(); onNavigate('docs'); }}>API Reference</a>
          <a href="#settings" onClick={(e) => { e.preventDefault(); onNavigate('settings'); }}>Settings</a>
        </div>
      </footer>
    </div>
  );
}
