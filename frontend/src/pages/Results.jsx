import React, { useState, useMemo } from 'react';
import NoveltyGauge from '../components/NoveltyGauge';
import PatentCard from '../components/PatentCard';
import GapCard from '../components/GapCard';
import { Icon } from '../components/Icons';

// Simple Markdown formatting helper for the generative LLM response
function formatMarkdown(text) {
  if (!text) return '';
  
  let formatted = text
    .replace(/^-\s+(.*)$/gmi, '<li>$1</li>')
    .replace(/^\*\s+(.*)$/gmi, '<li>$1</li>');
  
  const lines = formatted.split('\n');
  let inList = false;
  const processedLines = [];
  
  for (let line of lines) {
    const trimmed = line.trim();
    const isLi = trimmed.startsWith('<li>') || trimmed.startsWith('</li>');
    if (isLi && !inList) {
      processedLines.push('<ul style="margin-left: 20px; margin-bottom: 12px; list-style-type: disc;">');
      inList = true;
    } else if (!isLi && inList) {
      processedLines.push('</ul>');
      inList = false;
    }
    processedLines.push(line);
  }
  if (inList) {
    processedLines.push('</ul>');
  }
  
  formatted = processedLines.join('\n');
  
  formatted = formatted
    .replace(/^### (.*)$/gmi, '<h4 style="color:#fff; margin:16px 0 8px 0; font-weight:600; font-size:14px;">$1</h4>')
    .replace(/^## (.*)$/gmi, '<h3 style="color:#fff; margin:20px 0 10px 0; font-weight:600; font-size:16px; border-bottom: 1px solid var(--border-neutral); padding-bottom: 4px;">$1</h3>')
    .replace(/^# (.*)$/gmi, '<h2 style="color:#fff; margin:24px 0 12px 0; font-weight:700; font-size:18px;">$1</h2>');
  
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  formatted = formatted
    .split('\n\n')
    .map(p => {
      const trimmed = p.trim();
      if (trimmed.startsWith('<h') || trimmed.startsWith('<ul') || trimmed.startsWith('<li') || trimmed.startsWith('</ul') || trimmed.startsWith('<p')) {
        return p;
      }
      return `<p style="margin-bottom: 12px; line-height: 1.6;">${p}</p>`;
    })
    .join('\n');
    
  return formatted;
}

export default function Results({ data, onNavigate, onStartComparison, onDeepDive }) {
  const [selectedConcept, setSelectedConcept] = useState(null);
  const [selectedYear, setSelectedYear] = useState(null);
  const [highlightedPatentId, setHighlightedPatentId] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedPatents, setSelectedPatents] = useState([]);
  const [selectionWarning, setSelectionWarning] = useState(null);

  // Extract variables safely before hooks
  const domain = data?.technology_domain || {};
  const primaryDomain = domain.primary_domain || 'GENERAL';
  const keyConcepts = domain.key_concepts || [];
  const patents = useMemo(() => data?.evidence_ranking || data?.similar_patents || [], [data]);
  const novelty = data?.novelty_score || {};
  const noveltyScore = Number(novelty.score ?? novelty.novelty_score ?? novelty.overall_novelty_score ?? 0);
  const gaps = data?.innovation_gaps || [];
  const confidence = data?.confidence_score || {};
  
  const analysisHtml = useMemo(() => formatMarkdown(data?.analysis), [data?.analysis]);

  // Extract unique assignee companies and calculate counts
  const competitorStats = useMemo(() => {
    const counts = {};
    patents.forEach(p => {
      const name = p.applicant_name || 'Unknown';
      counts[name] = (counts[name] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  }, [patents]);

  // Extract patent years and map them for timeline
  const patentYears = useMemo(() => {
    const yearMap = {};
    patents.forEach(p => {
      const appNum = p.application_number || '';
      const match = appNum.match(/\b(19|20)\d{2}\b/);
      if (match) {
        const yr = match[0];
        if (!yearMap[yr]) yearMap[yr] = [];
        yearMap[yr].push(p);
      }
    });
    return Object.entries(yearMap)
      .map(([year, list]) => ({ year, patents: list }))
      .sort((a, b) => Number(a.year) - Number(b.year));
  }, [patents]);

  // Filter patents based on active concept filter
  const filteredPatents = useMemo(() => {
    return patents.filter(p => {
      if (!selectedConcept) return true;
      const conceptLower = selectedConcept.toLowerCase();
      const titleLower = (p.title || '').toLowerCase();
      const textLower = (p.patent_text || '').toLowerCase();
      const fieldLower = (p.field_of_invention || '').toLowerCase();
      return titleLower.includes(conceptLower) || textLower.includes(conceptLower) || fieldLower.includes(conceptLower);
    });
  }, [patents, selectedConcept]);

  // Network graph calculations (SVG)
  const graphNodes = useMemo(() => {
    const center = { x: 230, y: 130, label: 'My Idea', isCenter: true };
    const list = [center];
    const count = patents.length;

    patents.forEach((p, idx) => {
      const angle = (idx * 2 * Math.PI) / count;
      const similarity = p.similarity_score || 0.5;
      const distance = 160 - similarity * 80; 
      
      list.push({
        x: 230 + Math.cos(angle) * distance,
        y: 130 + Math.sin(angle) * distance * 0.75,
        label: `P${idx + 1}`,
        similarity: Math.round(similarity * 100),
        title: p.title,
        applicant: p.applicant_name,
        appNum: p.application_number,
        isCenter: false
      });
    });

    return list;
  }, [patents]);

  const togglePatentSelection = (patent) => {
    setSelectionWarning(null);
    const pid = patent.publication_number || patent.application_number;
    const isSelected = selectedPatents.some(p => (p.publication_number || p.application_number) === pid);
    if (isSelected) {
      setSelectedPatents(prev => prev.filter(p => (p.publication_number || p.application_number) !== pid));
    } else {
      if (selectedPatents.length >= 3) {
        setSelectionWarning('Comparison is limited to 3 patents.');
        return;
      }
      setSelectedPatents(prev => [...prev, patent]);
    }
  };

  const triggerHighlight = (appNum) => {
    const elementId = `patent-${appNum.replace(/[^a-zA-Z0-9]/g, '-')}`;
    const el = document.getElementById(elementId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setHighlightedPatentId(appNum);
      setTimeout(() => {
        setHighlightedPatentId(null);
      }, 2500);
    }
  };

  const handleYearClick = (year) => {
    setSelectedYear(selectedYear === year ? null : year);
    const matchedPatent = patents.find(p => {
      const match = (p.application_number || '').match(/\b(19|20)\d{2}\b/);
      return match && match[0] === year;
    });
    if (matchedPatent) {
      triggerHighlight(matchedPatent.application_number);
    }
  };

  const handleConceptClick = (concept) => {
    setSelectedConcept(selectedConcept === concept ? null : concept);
  };

  const clearFilters = () => {
    setSelectedConcept(null);
    setSelectedYear(null);
  };

  // If no analysis is loaded, display standard placeholder
  if (!data) {
    return (
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div className="panel panel-padding" style={{ width: '100%', maxWidth: '480px', textAlign: 'center', background: 'var(--bg-surface)' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="search" size={24} color="var(--primary)" />
            </div>
          </div>
          <h2 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
            No Analysis Loaded
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: '1.6' }}>
            Submit an invention description in the Patent Search workspace to view prior-art metrics, proximity graphs, and landscape analysis.
          </p>
          <button className="btn-primary" onClick={() => onNavigate('workspace')}>
            Open Patent Search
            <Icon name="arrow-right" size={14} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ margin: '16px auto' }}>
      {/* Top Header Toolbar */}
      <div className="results-toolbar">
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Patent Intelligence Center
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Deep-dive landscape metrics, novelty indicators, and technology whitespace mapping.
          </p>
        </div>
      </div>

      {/* Summary Metrics Bar */}
      <div className="summary-bar">
        <div className="summary-stat-box">
          <div className="summary-stat-label">Technology Class</div>
          <div className="summary-stat-value" style={{ textTransform: 'uppercase' }}>{primaryDomain}</div>
        </div>
        <div className="summary-stat-box">
          <div className="summary-stat-label">AI Novelty Indicator</div>
          <div className="summary-stat-value" style={{ color: 'var(--primary)' }}>{noveltyScore}%</div>
        </div>
        <div className="summary-stat-box">
          <div className="summary-stat-label">Confidence Rating</div>
          <div className="summary-stat-value" style={{ 
            color: confidence.confidence_rating?.toLowerCase() === 'high' ? 'var(--success)' : 
                   confidence.confidence_rating?.toLowerCase() === 'medium' ? 'var(--warning)' : 'var(--error)'
          }}>
            {confidence.confidence_rating || 'MEDIUM'}
          </div>
        </div>
        <div className="summary-stat-box">
          <div className="summary-stat-label">Prior Art Located</div>
          <div className="summary-stat-value">{patents.length} Patents</div>
        </div>
        <div className="summary-stat-box">
          <div className="summary-stat-label">Innovation Gaps</div>
          <div className="summary-stat-value" style={{ color: 'var(--accent-violet)' }}>{gaps.length} Whitespaces</div>
        </div>
      </div>

      {/* First Grid Row: Novelty Assessment & Patent Graph */}
      <div className="dashboard-row">
        {/* Novelty Score Dial */}
        <div className="panel panel-padding">
          <h2 className="panel-title">{novelty.indicator_name || "AI-Estimated Novelty Indicator"}</h2>
          <div className="novelty-flex-container">
            <div className="novelty-stat">
              <NoveltyGauge score={noveltyScore} />
              <span className={`novelty-status-pill ${
                (novelty.band || '').toLowerCase().includes('highly') || (novelty.band || '').toLowerCase().includes('strong') ? 'high' : 
                (novelty.band || '').toLowerCase().includes('moderate') || (novelty.band || '').toLowerCase().includes('medium') ? 'medium' : 'low'
              }`}>
                {novelty.band || 'Moderate'}
              </span>
            </div>
            <div className="novelty-description-box">
              <p style={{ marginBottom: '12px' }}>{novelty.explanation}</p>
              {novelty.breakdown && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', fontSize: '11px', marginTop: '14px', background: 'var(--bg-surface-secondary)', padding: '10px', borderRadius: 'var(--border-radius-md)' }}>
                  <div>Uniqueness: <strong>{Math.round(novelty.breakdown.concept_uniqueness || 0)}%</strong></div>
                  <div>Saturation: <strong>{Math.round(100 - (novelty.breakdown.domain_saturation || 0))}%</strong></div>
                  <div>Diff: <strong>{Math.round(100 - (novelty.breakdown.similarity_overlap || 0) * 100)}%</strong></div>
                </div>
              )}
              {novelty.disclaimer && (
                <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "12px", fontStyle: "italic", borderTop: "1px solid var(--border-neutral)", paddingTop: "8px" }}>
                  {novelty.disclaimer}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Interactive SVG Patent Graph */}
        <div className="panel panel-padding" style={{ position: 'relative', overflow: 'hidden' }}>
          <h2 className="panel-title">Patent Proximity Graph</h2>
          <div style={{ display: 'flex', position: 'relative', height: '240px' }}>
            <svg width="100%" height="240px" style={{ overflow: 'visible' }}>
              {/* Draw Links */}
              {graphNodes.slice(1).map((node, idx) => (
                <line
                  key={idx}
                  x1={graphNodes[0].x}
                  y1={graphNodes[0].y}
                  x2={node.x}
                  y2={node.y}
                  stroke="rgba(110, 168, 254, 0.2)"
                  strokeWidth={1.5 + (node.similarity / 100) * 2.5}
                  strokeDasharray={node.appNum === hoveredNode?.appNum ? '4 4' : 'none'}
                />
              ))}

              {/* Draw Center Node */}
              <circle
                cx={graphNodes[0].x}
                cy={graphNodes[0].y}
                r="18"
                fill="var(--primary)"
                stroke="#fff"
                strokeWidth="1.5"
                style={{ cursor: 'default' }}
              />
              <text
                x={graphNodes[0].x}
                y={graphNodes[0].y + 4}
                fill="#080B12"
                fontSize="10"
                fontWeight="700"
                textAnchor="middle"
              >
                Idea
              </text>

              {/* Draw Surrounding Nodes */}
              {graphNodes.slice(1).map((node, idx) => (
                <g 
                  key={idx}
                  onMouseEnter={() => setHoveredNode(node)}
                  onMouseLeave={() => setHoveredNode(null)}
                  onClick={() => triggerHighlight(node.appNum)}
                  style={{ cursor: 'pointer' }}
                >
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r="13"
                    fill="var(--bg-surface-secondary)"
                    stroke={hoveredNode?.appNum === node.appNum ? 'var(--primary)' : 'var(--border-neutral)'}
                    strokeWidth="1.5"
                  />
                  <text
                    x={node.x}
                    y={node.y + 3.5}
                    fill="var(--text-secondary)"
                    fontSize="9.5"
                    fontWeight="600"
                    textAnchor="middle"
                  >
                    {node.label}
                  </text>
                </g>
              ))}
            </svg>

            {/* Hover Tooltip Overlay */}
            {hoveredNode ? (
              <div style={{
                position: 'absolute',
                bottom: '10px',
                left: '10px',
                right: '10px',
                background: 'var(--bg-surface-elevated)',
                border: '1px solid var(--border-neutral)',
                borderRadius: 'var(--border-radius-md)',
                padding: '8px 12px',
                fontSize: '11px',
                pointerEvents: 'none',
                zIndex: 10
              }}>
                <span style={{ color: 'var(--primary)', fontWeight: 600, display: 'block', textTransform: 'uppercase', fontSize: '9px', marginBottom: '2px' }}>
                  {hoveredNode.appNum} • Match: {hoveredNode.similarity}%
                </span>
                <strong style={{ color: 'var(--text-primary)', display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {hoveredNode.title}
                </strong>
                <span style={{ color: 'var(--text-secondary)' }}>Applicant: {hoveredNode.applicant}</span>
              </div>
            ) : (
              <div style={{
                position: 'absolute',
                bottom: '10px',
                right: '10px',
                fontSize: '10px',
                color: 'var(--text-muted)'
              }}>
                Hover nodes for summary • Click to navigate
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Competitor Landscape & Chronological Timeline */}
      <div className="dashboard-row">
        {/* Competitor Intelligence */}
        <div className="panel panel-padding">
          <h2 className="panel-title">Competitor Landscape</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Top assignee organizations holding related prior art documents:
          </p>
          <div className="competitor-list">
            {competitorStats.map((item, idx) => (
              <div key={idx} className="competitor-row">
                <span className="competitor-name">{item.name}</span>
                <span className="competitor-count">{item.count} {item.count === 1 ? 'patent' : 'patents'}</span>
              </div>
            ))}
            {competitorStats.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '24px' }}>
                No competitor applicants identified.
              </div>
            )}
          </div>
        </div>

        {/* Timeline Evolution */}
        {patentYears.length > 0 && (
          <div className="panel panel-padding">
            <h2 className="panel-title">Patent Chronological Evolution</h2>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
              Chronological year timeline nodes. Click node to highlight relevant patent abstract details:
            </p>
            
            <div className="timeline-track">
              <div className="timeline-line"></div>
              <div className="timeline-nodes">
                {patentYears.map((item, idx) => (
                  <div 
                    key={idx} 
                    className="timeline-node-item" 
                    onClick={() => handleYearClick(item.year)}
                  >
                    <span className="timeline-year">{item.year}</span>
                    <div 
                      className="timeline-node-circle"
                      style={{
                        backgroundColor: selectedYear === item.year ? 'var(--primary)' : 'var(--bg-base)',
                        transform: selectedYear === item.year ? 'scale(1.3)' : 'scale(1)'
                      }}
                    />
                    <div className="timeline-node-info">
                      {item.patents.length} {item.patents.length === 1 ? 'Doc' : 'Docs'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Concept Filters & Executive Report layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '20px', marginBottom: '24px' }}>
        
        {/* Left Side: Landscape Filter Chips & Gaps */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Key Concept Filters */}
          <div className="panel panel-padding">
            <h2 className="panel-title">Interactive Concepts</h2>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
              Filter prior art list by selecting key technical parameters:
            </p>
            <div className="landscape-chips-wrapper">
              {keyConcepts.map((concept, idx) => {
                const isSelected = selectedConcept === concept;
                return (
                  <button
                    key={idx}
                    className={`landscape-chip ${isSelected ? 'active' : ''}`}
                    onClick={() => handleConceptClick(concept)}
                    style={{
                      background: isSelected ? 'var(--primary)' : 'var(--bg-surface-secondary)',
                      color: isSelected ? '#080B12' : 'var(--text-secondary)',
                      border: '1px solid var(--border-neutral)',
                      cursor: 'pointer',
                      transition: 'all var(--transition-fast)'
                    }}
                  >
                    {concept}
                  </button>
                );
              })}
            </div>
            
            {(selectedConcept || selectedYear) && (
              <button 
                className="btn-secondary" 
                onClick={clearFilters}
                style={{ width: '100%', padding: '6px', fontSize: '12px', marginTop: '6px' }}
              >
                Clear Active Filters
              </button>
            )}
          </div>

          {/* Whitespace Innovation Opportunities */}
          <div>
            <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Whitespace Gap Detections
            </h3>
            {gaps.map((gap, idx) => (
              <GapCard key={idx} gap={gap} />
            ))}
          </div>
        </div>

        {/* Right Side: RAG Executive Summary */}
        <div className="panel panel-padding">
          <h2 className="panel-title">Executive Intelligence Report</h2>
          <div 
            className="rag-analysis-content"
            dangerouslySetInnerHTML={{ __html: analysisHtml }}
            style={{ 
              color: 'var(--text-secondary)', 
              fontSize: '13.5px', 
              lineHeight: '1.7' 
            }}
          />
        </div>
      </div>

      {/* Prior Art Patents Details */}
      <section style={{ marginTop: '24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Semantically Aligned Patents ({filteredPatents.length})</span>
          {selectedConcept && (
            <span style={{ fontSize: '12px', fontWeight: 400, color: 'var(--primary-light)' }}>
              Filtering by: "{selectedConcept}"
            </span>
          )}
        </h2>

        {/* Floating / Sticky Comparison Action Bar */}
        {selectedPatents.length > 0 && (
          <div 
            style={{
              position: 'sticky',
              top: '64px',
              zIndex: 50,
              background: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-active)',
              boxShadow: 'var(--shadow-lg)',
              borderRadius: 'var(--border-radius-md)',
              padding: '10px 18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '16px',
              marginBottom: '16px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Icon name="compare" size={16} color="var(--primary)" />
                <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {selectedPatents.length} {selectedPatents.length === 1 ? 'patent' : 'patents'} selected
                </span>
              </div>
              {selectedPatents.length < 2 && (
                <span style={{ fontSize: '11px', color: 'var(--warning)', background: 'var(--warning-glow)', padding: '2px 8px', borderRadius: '4px' }}>
                  Select at least 2 patents to compare
                </span>
              )}
              {selectionWarning && (
                <span style={{ fontSize: '11px', color: 'var(--error)', background: 'var(--error-glow)', padding: '2px 8px', borderRadius: '4px' }}>
                  {selectionWarning}
                </span>
              )}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button 
                className="btn-secondary" 
                onClick={() => { setSelectedPatents([]); setSelectionWarning(null); }}
                style={{ padding: '6px 12px', fontSize: '12px' }}
              >
                Clear
              </button>
              <button 
                className="btn-primary" 
                disabled={selectedPatents.length < 2 || selectedPatents.length > 3}
                onClick={() => onStartComparison && onStartComparison(selectedPatents)}
                style={{ 
                  padding: '6px 14px', 
                  fontSize: '12.5px', 
                  opacity: selectedPatents.length < 2 ? 0.5 : 1,
                  cursor: selectedPatents.length < 2 ? 'not-allowed' : 'pointer'
                }}
              >
                Compare Selected ({selectedPatents.length}/3)
                <Icon name="arrow-right" size={13} color="#080B12" />
              </button>
            </div>
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {filteredPatents.map((pat, idx) => {
            const isSelected = selectedPatents.some(p => (p.publication_number || p.application_number) === (pat.publication_number || pat.application_number));
            return (
              <PatentCard 
                key={idx} 
                patent={pat} 
                highlightClass={highlightedPatentId === pat.application_number ? 'highlight-flash' : ''}
                selectable={true}
                selected={isSelected}
                onToggleSelect={togglePatentSelection}
                onDeepDive={onDeepDive}
              />
            );
          })}
          {filteredPatents.length === 0 && (
            <div className="panel panel-padding" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              No patents match the current filters. Click "Clear Active Filters" above.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
