import React, { useEffect, useState } from 'react';

const STEPS = [
  "Understanding Technical Idea",
  "Searching Patent Vector Index",
  "Filtering Prior Art & Competitors",
  "Calculating Novelty Percentages",
  "Synthesizing Gemini RAG Report"
];

export default function Analysis() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    // Sequentially advance steps to simulate a detailed pipeline progress
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < STEPS.length - 1) {
          return prev + 1;
        }
        return prev; // Hold on last step until parent switches views
      });
    }, 900);

    return () => clearInterval(interval);
  }, []);

  const progressPercentage = ((currentStep + 1) / STEPS.length) * 100;

  return (
    <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
      <div className="panel analysis-panel" style={{ width: '100%', maxWidth: '480px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px', textAlign: 'center' }}>
          Running PatentIQ Pipeline
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '24px', textAlign: 'center' }}>
          Embedding input description and executing retrieval intelligence...
        </p>

        {/* Progress Track & Bar */}
        <div className="progress-track">
          <div 
            className="progress-bar" 
            style={{ 
              width: `${progressPercentage}%`,
              transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          />
        </div>

        {/* Checklist Steps */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {STEPS.map((step, idx) => {
            let statusClass = '';
            let indicatorText = idx + 1;
            
            if (idx < currentStep) {
              statusClass = 'completed';
              indicatorText = '✓';
            } else if (idx === currentStep) {
              statusClass = 'active';
            }

            return (
              <div key={idx} className={`step-item ${statusClass}`}>
                <div className="step-icon">
                  {indicatorText}
                </div>
                <span style={{ fontWeight: idx === currentStep ? '500' : '400' }}>
                  {step}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
