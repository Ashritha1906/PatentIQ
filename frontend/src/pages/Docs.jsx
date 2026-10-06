import React from 'react';

export default function Docs() {
  return (
    <div className="container" style={{ maxWidth: '900px', margin: '40px auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
          Reference Guide
        </span>
        <h1 style={{ fontSize: '26px', fontWeight: 700, color: '#fff' }}>Platform Documentation</h1>
      </div>

      {/* API Reference */}
      <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#fff', marginBottom: '16px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '8px' }}>
          Backend REST API Specifications
        </h2>
        <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          PatentIQ exposes standard HTTP endpoints built on FastAPI. These can be integrated into external workflows or scripts:
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Endpoint 1 */}
          <div style={{ border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)', padding: '12px 16px', background: 'var(--bg-surface-secondary)' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ background: 'var(--success)', color: '#fff', fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: '4px' }}>GET</span>
              <strong style={{ fontSize: '14px', color: '#fff' }}>/api/health</strong>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>
              Returns runtime checkups indicating if ChromaDB is active, collection size, and LLM simulation configurations.
            </p>
          </div>

          {/* Endpoint 2 */}
          <div style={{ border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)', padding: '12px 16px', background: 'var(--bg-surface-secondary)' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ background: 'var(--primary)', color: '#fff', fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: '4px' }}>POST</span>
              <strong style={{ fontSize: '14px', color: '#fff' }}>/api/search</strong>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Performs raw semantic matching against ChromaDB.
            </p>
            <pre style={{ background: 'var(--bg-base)', padding: '10px', borderRadius: '4px', fontSize: '11px', color: 'var(--text-secondary)', overflowX: 'auto' }}>
{`Payload: { "idea_text": "string", "top_k": 5 }
Response: [ { "application_number": "string", "title": "string", "similarity_score": 0.85, ... } ]`}
            </pre>
          </div>

          {/* Endpoint 3 */}
          <div style={{ border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)', padding: '12px 16px', background: 'var(--bg-surface-secondary)' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ background: 'var(--primary)', color: '#fff', fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: '4px' }}>POST</span>
              <strong style={{ fontSize: '14px', color: '#fff' }}>/api/analyze</strong>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Executes the full RAG analytical intelligence orchestrator. Returns structured reports, novelty calculations, and white-space opportunity lists.
            </p>
            <pre style={{ background: 'var(--bg-base)', padding: '10px', borderRadius: '4px', fontSize: '11px', color: 'var(--text-secondary)', overflowX: 'auto' }}>
{`Payload: { "idea_text": "string", "top_k": 5, "domain_filter": null, "applicant_filter": null }
Response: { "user_idea": "string", "novelty_score": { "score": 85, ... }, "similar_patents": [...], "innovation_gaps": [...] }`}
            </pre>
          </div>
        </div>
      </div>

      {/* RAG Pipeline Flow */}
      <div className="panel panel-padding" style={{ background: 'var(--bg-surface)', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#fff', marginBottom: '16px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '8px' }}>
          RAG Pipeline Architecture
        </h2>
        <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: '1.6', marginBottom: '16px' }}>
          Our advanced Retrieval-Augmented Generation (RAG) system incorporates multiple filters and processors to minimize model hallucinations and ensure data compliance:
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div style={{ padding: '14px', background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)' }}>
            <strong style={{ display: 'block', color: 'var(--primary-light)', fontSize: '14px', marginBottom: '6px' }}>1. Local Embeddings</strong>
            <span style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>
              Encodes invention queries using Sentence Transformers (`all-MiniLM-L6-v2`) to output 384-dimensional vector spaces.
            </span>
          </div>
          <div style={{ padding: '14px', background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)' }}>
            <strong style={{ display: 'block', color: 'var(--primary-light)', fontSize: '14px', marginBottom: '6px' }}>2. Vector Filtering</strong>
            <span style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>
              Retrieves candidates in ChromaDB, applying boolean metadata filters (Applicant and Domain classes) when requested.
            </span>
          </div>
          <div style={{ padding: '14px', background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)' }}>
            <strong style={{ display: 'block', color: 'var(--primary-light)', fontSize: '14px', marginBottom: '6px' }}>3. Evidence Ranking</strong>
            <span style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>
              Scores patents dynamically based on a weighted sum of semantic similarity (50%), concept match (20%), domain (20%), and metadata (10%).
            </span>
          </div>
          <div style={{ padding: '14px', background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)' }}>
            <strong style={{ display: 'block', color: 'var(--primary-light)', fontSize: '14px', marginBottom: '6px' }}>4. Context Prompting</strong>
            <span style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>
              Compresses patent abstracts into tight context blocks to stay under Gemini token limits and prevent Hallucinations.
            </span>
          </div>
        </div>
      </div>

      {/* FAQ Sheets */}
      <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#fff', marginBottom: '16px', borderBottom: '1px solid var(--border-neutral)', paddingBottom: '8px' }}>
          Frequently Asked Questions
        </h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {/* FAQ 1 */}
          <details style={{ border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)', padding: '10px 14px', background: 'var(--bg-surface-secondary)' }}>
            <summary style={{ fontWeight: 600, fontSize: '14px', color: '#fff', cursor: 'pointer', outline: 'none' }}>
              Where does the patent dataset come from?
            </summary>
            <p style={{ marginTop: '8px', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              PatentIQ indexes a customized database comprising over 115,000 patent documents spanning electronics, software engineering, bio-medical devices, and automotive designs. The vector database is managed locally via ChromaDB.
            </p>
          </details>

          {/* FAQ 2 */}
          <details style={{ border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)', padding: '10px 14px', background: 'var(--bg-surface-secondary)' }}>
            <summary style={{ fontWeight: 600, fontSize: '14px', color: '#fff', cursor: 'pointer', outline: 'none' }}>
              How is the Novelty Score calculated?
            </summary>
            <p style={{ marginTop: '8px', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              The novelty score is calculated programmatically using a combination of average vector similarity overlap, key concepts uniqueness (how many proposed concepts are unmentioned in prior art), and domain saturation curves.
            </p>
          </details>

          {/* FAQ 3 */}
          <details style={{ border: '1px solid var(--border-neutral)', borderRadius: 'var(--border-radius-md)', padding: '10px 14px', background: 'var(--bg-surface-secondary)' }}>
            <summary style={{ fontWeight: 600, fontSize: '14px', color: '#fff', cursor: 'pointer', outline: 'none' }}>
              How does the interactive patent graph help?
            </summary>
            <p style={{ marginTop: '8px', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              The patent graph represents the semantic distance between your invention (center node) and surrounding prior art (peripheral nodes). Thick, shorter connecting lines indicate high similarity overlap. Clicking nodes scrolls you directly to the patent abstract text cards for details.
            </p>
          </details>
        </div>
      </div>
    </div>
  );
}
