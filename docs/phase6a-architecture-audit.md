# PatentIQ - Phase 6A Architecture Audit
## Natural Language Query Engine + Hybrid Patent Retrieval

**Audit Date:** 2026-10-06
**Corpus Scope:** 115,625 indexed Indian patent records (2010-2019)
**Embeddings:** 384-dimensional dense vectors (all-MiniLM-L6-v2), L2-normalized
**Vector Store:** Persistent ChromaDB (data/vectordb, collection patentiq_patents, cosine distance space)
**Status:** Audit Completed prior to Phase 6A implementation

---

## 1. Existing Search Architecture

PatentIQ currently possesses a multi-tier patent analytics platform:

### 1.1 Ingestion & Vector Storage
* **Dataset:** 115,625 records stored in data/processed/patent_text_dataset.csv and corresponding precomputed embeddings in data/processed/patent_embeddings.npy (177.6 MB).
* **ChromaDB Vector Store:** Located in data/vectordb/. Initialized via PersistentClient(path='data/vectordb') containing collection patentiq_patents configured with {'hnsw:space': 'cosine'}.
* **Stored Metadatas:** Each document in ChromaDB stores:
  * application_number: Canonical unique patent application identifier (e.g. 1/CHE/2010).
  * title: Patent title in English uppercase.
  * field_of_invention: Broad engineering/scientific domain (e.g. COMPUTER SCIENCE, PHARMACEUTICALS, COMMUNICATION, MECHANICAL ENGINEERING).
  * classification_ipc: Primary International Patent Classification code (e.g. A61K, G06F, H04L).
  * applicant_name: Assignee/applicant corporate or individual entity name.
  * Document body: Text concatenation of Title, Field, Classification, and Abstract/Claims summary.

### 1.2 Embedding Service
* **Model:** sentence-transformers/all-MiniLM-L6-v2.
* **Caching & Lifecycle:** Loaded lazily through backend/retrieval/search_patents.py::get_retrieval_resources(). Caches _model_cache and _collection_cache globally in memory across requests.

### 1.3 Retrieval Components
* **Pure Semantic Search (backend/retrieval/search_patents.py):**
  * Computes 384-D query embedding using model.encode(query, convert_to_numpy=True).
  * Executes collection.query(query_embeddings=[query_embedding], n_results=top_k).
  * Returns cosine similarity score as 1.0 - distance where distance is Chroma cosine distance.
* **Hybrid Search (backend/retrieval/hybrid_search.py):**
  * Applies ChromaDB metadata pre-filters on field_of_invention, classification_ipc, and applicant_name via Chroma where clause.
  * Implements fallback logic: if strict metadata filters yield 0 results, it falls back to unfiltered semantic search to prevent empty result sets.
  * Note on Keyword Search: The existing backend/retrieval/hybrid_search.py does not yet execute a full lexical/keyword inverted retrieval track (it only applies metadata equality filters). In Phase 6A, we extend this by adding a true lexical/keyword retrieval component that scores documents by technical phrase and concept overlap.
* **VectorStore Abstraction (backend/api/services/vector_store.py):**
  * Defines VectorStore(ABC) with abstract methods search(), insert(), delete().
  * Defines ChromaVectorStore(VectorStore) delegating to backend.retrieval.hybrid_search.
* **Evidence Ranker (backend/rag/evidence_ranker.py):**
  * Calculates an Evidence Score (0-100) combining:
    * Semantic similarity (50% weight)
    * Keyword/concept coverage in title and document text (20% weight)
    * Domain alignment mapping technology categories to allowed fields (20% weight)
    * Metadata relevance matching applicant or IPC (10% weight)

### 1.4 RAG Pipeline & Gemini Integration
* **Gemini Client (backend/llm/gemini_client.py):**
  * Integrates google.generativeai with model gemini-2.5-flash.
  * Includes automatic fallback to simulated mock responses when MOCK_LLM=True or API key is absent.
  * Enforces rate limiting with a thread lock and minimum 12.5s spacing between calls to adhere to Free Tier 5 RPM limits, with exponential backoff retries.
* **Query Understanding (backend/llm/query_understanding.py):**
  * Calls Gemini to parse an invention idea into core_problem, technology_domain, key_concepts, keywords, optimized_query, metadata_hints.
* **RAG Context Retrieval & Compression (backend/rag/):**
  * retrieve_context.py: Orchestrates idea understanding -> vector search -> deduplication.
  * context_compressor.py: Compresses patent text into a concise token-budgeted prompt block.
  * context_summarizer.py: Extracts shared/unique concepts and technological themes across retrieved patents.
  * backend/llm/patent_analysis.py: Calls Gemini to generate structured novelty, overlap, and innovation gap comparative reports.

### 1.5 FastAPI Backend
* Main app in backend/api/main.py.
* Endpoints:
  * GET /api/health: Vector DB status, record counts, and LLM mode.
  * POST /api/search: Accepts IdeaRequest (idea_text, top_k, domain_filter, applicant_filter) and returns patent list.
  * POST /api/novelty: Calculates novelty score breakdown and differentiation band.
  * POST /api/analyze: Full intelligence pipeline (retrieval, ranking, clustering, novelty, gap detection, Gemini analysis, confidence assessment).
  * POST /api/knowledge/*: Live knowledge expansion management.

### 1.6 Frontend
* React + Vite in frontend/ serving SPA.
* Main research workspace in frontend/src/pages/Workspace.jsx.
* Results visualization in frontend/src/pages/Results.jsx with PatentCard.jsx, NoveltyGauge.jsx, GapCard.jsx.

---

## 2. Existing Retrieval Flow

`
User Query -> /api/search or /api/analyze
  -> PatentIntelligenceService._retrieve_context()
  -> understand_query() (Gemini/Mock)
  -> ChromaVectorStore.search()
  -> ChromaDB cosine nearest neighbor query
  -> Deduplication (by application_number and title)
  -> Top-K context patents
  -> (For /analyze: evidence_ranker -> context_compressor -> analyze_invention_novelty via Gemini -> response)
`

---

## 3. Existing Reusable Components

The following components are production-ready and will be reused without replacement:
1. backend/retrieval/search_patents.py::get_retrieval_resources(): Global singleton loader for all-MiniLM-L6-v2 and ChromaDB persistent collection.
2. backend/vectordb/chroma_store.py: Ingested collection patentiq_patents with 115,625 records.
3. VectorStore ABC and ChromaVectorStore in backend/api/services/vector_store.py.
4. backend/llm/gemini_client.py: Robust Gemini LLM execution client with mock generator, rate-limiting, and error-handling.
5. backend/rag/context_compressor.py: Token-budget context compression for RAG prompts.
6. backend/rag/evidence_ranker.py: Multi-factor scoring logic, domain alignment mappings, and breakdown calculation.
7. backend/api/services/orchestrator.py: Central PatentIntelligenceService managing search, novelty, and full analysis workflows.
8. backend/api/main.py: FastAPI application structure, CORS middleware, and static asset serving.

---

## 4. Components That Must NOT Be Duplicated

* DO NOT create a second ChromaDB client or collection.
* DO NOT regenerate embeddings or introduce alternative embedding models (must remain all-MiniLM-L6-v2).
* DO NOT migrate to Qdrant or any other vector store.
* DO NOT create a second Gemini client or replace backend/llm/gemini_client.py.
* DO NOT rewrite the existing RAG pipeline or replace backend/rag/.
* DO NOT create duplicate FastAPI routers or parallel search apps.
* DO NOT implement live EPO retrieval (strictly reserved for Phase 6B).
* DO NOT redesign the frontend UI.

---

## 5. Exact Integration Points for Phase 6A

1. Step 2 & 3 - Natural Language Query Model (PatentQuery):
   * Create backend/retrieval/query_model.py defining PatentQuery with controlled intent enum (QueryIntent), technical concepts, expanded terms, search phrases, classification candidates, entities, constraints, and confidence score.
2. Step 4 & 5 - Query Understanding & LLM Query Planner:
   * Extend backend/llm/query_understanding.py with plan_patent_query(user_query: str) -> PatentQuery leveraging the existing Gemini client and structured JSON schema, with deterministic mock support.
   * Strict constraint: LLM only plans retrieval strategy; zero hallucination of patent numbers, facts, or fake citations.
3. Step 6 & 7 - Query Expansion & Classification Handling:
   * Create backend/retrieval/query_expansion.py to expand synonyms, technical abbreviations, and domain terms up to MAX_EXPANSION_TERMS (default: 8).
   * Validate candidate IPC/CPC classifications against indexed dataset codes; treat unvalidated codes as soft signals only.
4. Step 8, 9, 10, 11 & 12 - Dual-Track Hybrid Retrieval & Result Fusion:
   * Create backend/retrieval/nl_retrieval.py combining:
     * Semantic vector search using query embedding from existing all-MiniLM-L6-v2.
     * Keyword retrieval on technical concepts and search phrases.
     * Score normalization (Min-Max scaling) to bring semantic and keyword relevance to a uniform [0.0, 1.0] scale.
     * Reciprocal rank / weighted fusion and deduplication by canonical publication_number (application number).
5. Step 13, 14 & 15 - Explainable Re-Ranking & Top-K Control:
   * Re-rank fused candidates using semantic proximity, keyword overlap, title match, claims/abstract overlap, and classification alignment.
   * Produce explicit, human-readable ranking_reasons (e.g. ['strong semantic similarity', 'title contains core technology', 'concept overlap in abstract']).
   * Configurable thresholds: QUERY_CANDIDATE_K=50, FINAL_RESULT_K=20, RAG_CONTEXT_K=5.
6. Step 16 - Search Result Contract:
   * Return structured PatentSearchResult containing patent_id, publication_number, title, abstract, applicant, inventors, publication_date, classification, semantic_score, keyword_score, final_score, ranking_reasons, source, and source_url.
7. Step 17 & 18 - RAG Pipeline Integration & Traceable Citations:
   * Hook top RAG context candidates directly into the existing compress_context() and analyze_invention_novelty() pipeline without altering the RAG contracts.
8. Step 19, 20 & 21 - API Endpoints & Minimal Frontend Enhancement:
   * Extend POST /api/search to support NLSearchRequest ({'query': '...'}) while remaining 100% backward compatible with IdeaRequest ({'idea_text': '...'}).
   * Update frontend search input placeholder in Workspace.jsx to: 'Describe the technology or invention you want to research...' and display ranking_reasons in PatentCard.jsx.

---

## 6. Files Proposed for Modification

| File | Proposed Changes |
| :--- | :--- |
| backend/api/routes/search.py | Extend POST /api/search to accept NLSearchRequest (with query) as well as existing IdeaRequest (with idea_text), returning NLSearchResponse. |
| backend/api/schemas/api_schemas.py | Add Pydantic models: QueryIntent, PatentQuery, PatentSearchResult, NLSearchRequest, NLSearchResponse. |
| backend/api/services/orchestrator.py | Add search_natural_language() method to PatentIntelligenceService that coordinates query understanding, hybrid retrieval, fusion, and re-ranking. |
| backend/llm/query_understanding.py | Add plan_patent_query() returning structured PatentQuery object with controlled enum intents. |
| backend/llm/gemini_client.py | Add structured prompt handling in get_mock_response() for query planning queries when offline. |
| frontend/src/pages/Workspace.jsx | Update textarea placeholder to accept natural language invention queries. |
| frontend/src/components/PatentCard.jsx | Render explainable ranking_reasons and hybrid/semantic/keyword score indicators. |
| frontend/src/services/api.js | Add searchNaturalLanguage() API client call. |

---

## 7. Files Proposed for Creation

| File | Purpose |
| :--- | :--- |
| docs/phase6a-architecture-audit.md | This mandatory architecture audit document (Step 1). |
| backend/retrieval/query_model.py | Pydantic data models for structured query representation, controlled intents, and search result contract. |
| backend/retrieval/query_expansion.py | Controlled technical synonym and acronym query expansion with MAX_EXPANSION_TERMS bounds. |
| backend/retrieval/nl_retrieval.py | Natural language dual-track hybrid retrieval engine (semantic + keyword + MinMax score normalization + deduplication + re-ranking + ranking reasons). |
| backend/tests/test_phase6a_retrieval.py | Comprehensive test suite containing 21 tests covering all scenarios specified in Step 22. |
| backend/evaluation/phase6a_eval.py | Precision@K, Recall@K, MRR, and latency benchmark suite evaluating 25 natural language queries. |
| docs/phase6a-natural-language-search.md | Detailed Phase 6A technical documentation covering architecture, retrieval flow, evaluation, and known limitations. |

---
**Audit Approval:** Verified complete and compliant with Phase 6A specifications. Proceeding to Step 2.
