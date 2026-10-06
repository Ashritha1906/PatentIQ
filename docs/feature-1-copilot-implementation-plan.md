# PATENTIQ — FEATURE 1: AI RESEARCH COPILOT IMPLEMENTATION PLAN
**NLP Query Understanding • Session Context • Federated Prior Art • Voice Interaction**

---

## 1. Executive Summary & Goals

Feature 1 introduces the **PatentIQ AI Research Copilot**, an enterprise-grade conversational patent research assistant that integrates directly into the existing PatentIQ platform.

The Copilot allows users to interact through natural language text and voice, ask follow-up questions, request explanations and comparisons, inspect concept whitespace, explore differentiation paths, and receive strictly grounded answers with source provenance—without hallucinating patent numbers, dates, or legal patentability claims.

---

## 2. Existing Architecture & Reusability Audit

The existing system is frozen and verified:
- **Corpus & Embeddings**: ~115,625 Indian patent records, `sentence-transformers/all-MiniLM-L6-v2`, ChromaDB vector store.
- **Retrieval Engine (Phases 3 & 6A)**: `backend/retrieval/nl_retrieval.py` (`execute_nl_hybrid_search`), BM25 + dense semantic scoring, Reciprocal Rank Fusion, identifier normalization (`backend/retrieval/identifier_normalizer.py`).
- **Federated Multi-Source (Phase 6B)**: `backend/patent_sources/` (`LocalPatentSource`, `EPOPublicationSource`, `ResultFusion`, LRU cache, usage tracking, provenance tagging).
- **Intelligence & RAG (Phases 4 & 6A.1)**:
  - `backend/intelligence/novelty_scoring.py`: "AI-Estimated Novelty Indicator", canonical consistency, disclaimer protection.
  - `backend/intelligence/innovation_gap.py`: Semantic concept coverage (Strongly, Moderately, Weakly Represented, No Meaningful Evidence) and combination gaps.
  - `backend/llm/gemini_client.py`: Gemini client with 5 RPM rate limiting and graceful mock fallback.
  - `backend/llm/query_understanding.py`: Natural language query planner (`plan_patent_query`).
  - `backend/rag/context_compressor.py` and `evidence_ranker.py`: Context window compression and evidence ranking.
- **API & Orchestrator**:
  - `backend/api/services/orchestrator.py` (`PatentIntelligenceService`)
  - `backend/api/main.py`: FastAPI server serving endpoints and React SPA at root.
- **Frontend**:
  - React + Vite SPA, CSS design system (`Outfit` & `Inter`, dark slate palette `#090d16`), reusable `PatentCard.jsx` with provenance badges (`LOCAL`, `EPO LIVE`, `LOCAL + EPO`).

**Zero New Vector Databases, Zero Duplicate RAG Pipelines, Zero Framework Rewrites.**

---

## 3. Files to Be Created

1. `backend/copilot/__init__.py`: Package export.
2. `backend/copilot/models.py`:
   - Intent taxonomy enum (`PRIOR_ART_SEARCH`, `EXPLAIN`, `COMPARE`, `SUMMARIZE`, `WHITESPACE`, `IMPROVE_IDEA`, `FOLLOW_UP`, `REPORT`).
   - Request/response Pydantic models (`CopilotChatRequest`, `CopilotChatResponse`, `CopilotTurn`, `CopilotSessionState`, `ResearchContextSummary`).
3. `backend/copilot/context.py`:
   - In-memory session store with TTL cleanup, conversation turn history, active query, retrieved patents, selected patent, cached novelty/whitespace results.
4. `backend/copilot/intent.py`:
   - Lightweight intent classifier & query extractor (rule-based heuristic + fallback to existing `plan_patent_query`), concept extractor, entity/patent ID detector.
5. `backend/copilot/resolver.py`:
   - Lightweight reference resolver for pronouns and ordinal references ("which one is closest?", "the second patent", "why?", "explain that", "does it use CNN?").
6. `backend/copilot/service.py`:
   - `CopilotService`: Core orchestrator routing requests through existing `PatentIntelligenceService`, executing grounded synthesis, strictly enforcing anti-hallucination rules and novelty disclaimers.
7. `backend/api/routes/copilot.py`:
   - FastAPI endpoints (`POST /api/copilot/chat`, `GET /api/copilot/session/{id}`, `DELETE /api/copilot/session/{id}`).
8. `frontend/src/pages/Copilot.jsx`:
   - Research Copilot workspace: chat stream, suggested prompt chips, patent result cards (reusing `PatentCard`), collapsible Research Context Panel, voice input (Web Speech API) with live state, optional browser TTS audio synthesis.
9. `backend/tests/test_feature1_copilot.py`:
   - Comprehensive unit and integration test suite (20+ tests).
10. `docs/feature-1-copilot.md`:
    - Architecture, API specification, usage guide, grounding safeguards.
11. `docs/feature-1-copilot-implementation-report.md`:
    - Final completion report with test outputs and verification.

---

## 4. Files to Be Modified

1. `backend/api/main.py`:
   - Mount `backend.api.routes.copilot.router` under `/api`.
2. `frontend/src/services/api.js`:
   - Add `chatCopilot({ message, sessionId, sourceMode })` API client function.
3. `frontend/src/App.jsx`:
   - Add Copilot navigation item to `navItems` (`id: 'copilot'`, `label: 'AI Copilot'`).
   - Route `activeTab === 'copilot'` to `<Copilot />`.
4. `frontend/src/pages/Home.jsx`:
   - Add interactive action card linking directly to AI Research Copilot.

---

## 5. NLP & Intent Understanding Strategy

Taxonomy (8 discrete intents):
- `PRIOR_ART_SEARCH`: Search and retrieve patents matching an invention or concept.
- `EXPLAIN`: Break down a specific or closest patent in plain language.
- `COMPARE`: Perform technical comparison between two or more retrieved patents.
- `SUMMARIZE`: High-level synthesis of current retrieved prior-art collection.
- `WHITESPACE`: Analyze strongly vs weakly covered concepts and combination gaps.
- `IMPROVE_IDEA`: Suggest technical differentiation directions based on whitespace.
- `FOLLOW_UP`: Clarifying questions about previously retrieved patents or concepts.
- `REPORT`: Format a structured prior-art research summary.

Strategy:
- High-precision regex and heuristic pattern matching for common queries ("compare", "explain", "closest", "why", "whitespace", "different").
- If ambiguous or new topic, invokes existing `plan_patent_query` to extract technical concepts and domain.
- Never introduces heavy third-party NLP packages (e.g. spaCy/NLTK).

---

## 6. Conversation Context & Reference Resolution

Session state:
```python
class CopilotSessionState:
    session_id: str
    current_query: str
    technical_concepts: List[str]
    retrieved_patents: List[PatentSearchResult]
    selected_patent_idx: Optional[int]
    turns: List[CopilotTurn]
    novelty_summary: Optional[Dict[str, Any]]
    whitespace_summary: Optional[Dict[str, Any]]
    source_mode: str
```

Resolution rules:
- Ordinal resolution: "the first one", "second patent", "patent 3" -> index in `retrieved_patents`.
- Relative resolution: "the closest one", "most relevant" -> index 0 (top ranked).
- Anaphora: "it", "that patent", "this invention" -> `selected_patent` or top patent.
- New topic detection: If a message introduces brand new technical terms without referencing prior patents, triggers new retrieval and updates active context.

---

## 7. Grounded Answering & Anti-Hallucination Safeguards

1. **System Prompt Constraint**:
   - Instructs LLM to act strictly as PatentIQ Research Copilot.
   - Forbids inventing patent numbers, claims, applicants, or dates.
   - Forbids legal novelty/patentability assertions ("patentable", "guaranteed novelty").
   - Explicit fallback response when evidence is missing: *"The retrieved document does not provide enough evidence for me to confirm that."*
2. **Deterministic Fallback & Grounding**:
   - If the LLM is unavailable or quota-limited, deterministic rule-based generators synthesize answers directly from `retrieved_patents[i].abstract` and metadata.
3. **Novelty Disclaimers**:
   - Always applies: *"AI-Estimated Novelty Indicator: This is an automated prior-art similarity indicator and is not a legal determination of patentability or novelty."*

---

## 8. Voice Interaction & Audio Strategy

1. **Speech-to-Text (STT)**:
   - Uses Web Speech API (`window.webkitSpeechRecognition` || `window.SpeechRecognition`).
   - Browser-native, zero external API keys, zero cloud latency/billing.
   - Real-time visual states: "Listening...", "Transcribing...", error fallbacks.
   - Populates the chat textarea directly, allowing the user to review/edit before sending.
   - Graceful fallback: If browser does not support SpeechRecognition, mic icon shows tooltip and allows instant typing.
2. **Text-to-Speech (TTS)**:
   - Optional `Listen` speaker button on Copilot messages using `window.speechSynthesis`.
   - Toggle speech on/off cleanly.

---

## 9. Testing & Regression Strategy

1. **New Tests (`backend/tests/test_feature1_copilot.py`)**:
   - Intent classification tests across all 8 intents.
   - Follow-up and reference resolution tests ("which is closest", "why", "second patent").
   - Grounded evidence response checks (no hallucinations on unknown technical questions).
   - Novelty terminology and disclaimer preservation.
   - Empty queries and invalid sessions resilience.
   - LLM quota/failure graceful fallback.
   - API schema and endpoint validation.
2. **Regression Verification**:
   - `test_phase6a1_corrections.py` (14 tests) -> MUST PASS.
   - `test_phase6a_retrieval.py` (21 tests) -> MUST PASS.
   - `test_phase6b_federated_retrieval.py` (11 tests) -> MUST PASS.
   - Frontend Vite build (`npm run build`) -> MUST PASS.
