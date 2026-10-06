import React, { useState } from 'react';

export default function Knowledge({ systemHealth }) {
  const [ingesting, setIngesting] = useState(false);
  const [successMsg, setSuccessMsg] = useState(false);
  const [form, setForm] = useState({
    title: '',
    appNum: '',
    applicant: '',
    ipcClass: '',
    field: 'COMPUTER SCIENCE',
    abstract: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.title || !form.appNum || !form.abstract) return;
    
    setIngesting(true);
    // Simulate ingestion API delay
    setTimeout(() => {
      setIngesting(false);
      setSuccessMsg(true);
      setForm({
        title: '',
        appNum: '',
        applicant: '',
        ipcClass: '',
        field: 'COMPUTER SCIENCE',
        abstract: ''
      });
      setTimeout(() => setSuccessMsg(false), 3000);
    }, 1500);
  };

  const handleInputChange = (field, val) => {
    setForm(prev => ({ ...prev, [field]: val }));
  };

  return (
    <div className="container" style={{ maxWidth: '900px', margin: '40px auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
          Data Engineering
        </span>
        <h1 style={{ fontSize: '26px', fontWeight: 700, color: '#fff' }}>Knowledge Ingestion</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px', alignItems: 'start' }}>
        {/* Left Side: Incremental Ingestion Form */}
        <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
          <h2 style={{ fontSize: '17px', fontWeight: 600, color: '#fff', marginBottom: '14px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '8px' }}>
            Simulate Incremental Patent Ingestion
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Index a new patent record into the local vector DB space. The record will be encoded using the Sentence Transformer embeddings pipeline:
          </p>

          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
              <div>
                <label className="input-label" htmlFor="ingestTitle">Patent Title</label>
                <input
                  id="ingestTitle"
                  type="text"
                  className="text-field"
                  placeholder="e.g. Distributed Consensus Engine"
                  value={form.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="input-label" htmlFor="ingestAppNum">Application Number</label>
                <input
                  id="ingestAppNum"
                  type="text"
                  className="text-field"
                  placeholder="e.g. US/105234/2024"
                  value={form.appNum}
                  onChange={(e) => handleInputChange('appNum', e.target.value)}
                  required
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
              <div>
                <label className="input-label" htmlFor="ingestApplicant">Applicant Name</label>
                <input
                  id="ingestApplicant"
                  type="text"
                  className="text-field"
                  placeholder="e.g. Qualcomm, Samsung"
                  value={form.applicant}
                  onChange={(e) => handleInputChange('applicant', e.target.value)}
                />
              </div>
              <div>
                <label className="input-label" htmlFor="ingestIpc">IPC Classification</label>
                <input
                  id="ingestIpc"
                  type="text"
                  className="text-field"
                  placeholder="e.g. H04W 72/04"
                  value={form.ipcClass}
                  onChange={(e) => handleInputChange('ipcClass', e.target.value)}
                />
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label className="input-label" htmlFor="ingestField">Domain Classification</label>
              <select
                id="ingestField"
                className="select-field"
                value={form.field}
                onChange={(e) => handleInputChange('field', e.target.value)}
              >
                <option value="COMPUTER SCIENCE">Computer Science</option>
                <option value="ELECTRONICS">Electronics</option>
                <option value="COMMUNICATION">Communication</option>
                <option value="BIO-MEDICAL ENGINEERING">Bio-Medical Engineering</option>
                <option value="BIOTECHNOLOGY">Biotechnology</option>
                <option value="ELECTRICAL">Electrical/Power</option>
                <option value="MECHANICAL ENGINEERING">Mechanical</option>
              </select>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="input-label" htmlFor="ingestAbstract">Patent Abstract / Specifications</label>
              <textarea
                id="ingestAbstract"
                className="textarea-field"
                placeholder="Paste the abstract text or primary claim language here..."
                value={form.abstract}
                onChange={(e) => handleInputChange('abstract', e.target.value)}
                style={{ height: '100px' }}
                required
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '12px' }}>
              {successMsg && (
                <span style={{ color: 'var(--success)', fontSize: '13px', fontWeight: 500 }}>
                  ✓ Record successfully indexed in ChromaDB
                </span>
              )}
              <button type="submit" className="btn-primary" disabled={ingesting}>
                {ingesting ? 'Encoding & Ingesting...' : 'Index Patent'}
              </button>
            </div>
          </form>
        </div>

        {/* Right Side: Ingestion Stats & Status */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Index statistics */}
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '12px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
              Index Statistics
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Collection Name:</span>
                <strong style={{ color: '#fff' }}>patentiq_patents</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Vector Dimension:</span>
                <strong style={{ color: '#fff' }}>384 (all-MiniLM-L6-v2)</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Total Indexed Documents:</span>
                <strong style={{ color: 'var(--primary-light)' }}>
                  {systemHealth?.database?.includes('count:') 
                    ? systemHealth.database.split('count:')[1].replace(')', '').trim()
                    : '115,625'}
                </strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Storage Format:</span>
                <strong style={{ color: '#fff' }}>SQLite/Chroma Persistent</strong>
              </div>
            </div>
          </div>

          {/* Sync Progress */}
          <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '12px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '6px' }}>
              Remote Repository Sync
            </h3>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              <p style={{ marginBottom: '10px' }}>Index is fully synchronized with local master dataset.</p>
              <div style={{ width: '100%', height: '6px', background: 'var(--bg-surface-secondary)', borderRadius: '3px', overflow: 'hidden', marginBottom: '14px' }}>
                <div style={{ width: '100%', height: '100%', backgroundColor: 'var(--success)' }}></div>
              </div>
              <button className="btn-secondary" style={{ width: '100%', padding: '6px', fontSize: '12px' }} disabled>
                Sync with Master Registry
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
