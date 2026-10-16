# PATENTIQ — FEATURE 2: PATENT COMPARISON & DEEP-DIVE WORKSPACE IMPLEMENTATION PLAN
**Multi-Patent Technical Comparison • Concept Overlap Analysis • AI Deep Dive**

---

## 1. Executive Summary & Goals

Feature 2 builds a dedicated **Patent Comparison & Deep-Dive Workspace** directly on top of the verified PatentIQ platform and Feature 1 (AI Research Copilot).

It enables researchers to select 2 or 3 patents (from search results, Copilot turns, or direct selection) and generate a structured, evidence-grounded technical comparison covering:
- Core invention (problem solved, technical solution, central concept)
- Technical approaches (inputs, processing pipelines, AI/ML methods, outputs)
- Shared concepts & overlapping concept strength
- Distinct concepts within the comparison set
- Key technical differences & trade-offs
- Potential combination gaps (reusing Phase 6A.1 `detect_innovation_gaps`)
- Individual patent AI Deep-Dive (system flow, technical mechanisms, research questions, claim focus without legal construction)
- Technical similarity estimation (analytical metric, non-legal)

**Strict Rule Compliance**:
- Zero duplicate vector databases, RAG systems, embedding models, or retrieval engines.
- Research intelligence ONLY: never asserts patentability, legal infringement, freedom to operate, or validity.
- Grounded strictly in retrieved text and metadata; missing fields explicitly tagged as unavailable.

---

## 2. Existing Architecture & Reusability Audit

1. **Retrieval & Sources**:
   - `backend/retrieval/query_model.py`: `PatentSearchResult` contains `patent_id`, `publication_number`, `title`, `abstract`, `applicant`, `classification`, `source`, `semantic_score`, `provenance_metadata`.
   - `backend/patent_sources/`: `LocalPatentSource`, `EPOPublicationSource`, `ResultFusion` providing provenance (`LOCAL`, `EPO LIVE`, `LOCAL + EPO`).
2. **Intelligence & Whitespace**:
   - `backend/intelligence/innovation_gap.py`: `detect_innovation_gaps()` provides concept coverage and combination-gap analysis. Directly reused for Step 11.
3. **LLM & Grounding**:
   - `backend/llm/gemini_client.py`: `generate_text()` handles rate-limiting and graceful fallback.
4. **Feature 1 Copilot**:
   - `backend/copilot/service.py`: `CopilotService._handle_compare()` currently performs basic pairwise comparison. Feature 2 refactors this into the unified comparison engine so Copilot directly benefits from full 2–3 patent deep comparisons.
5. **Frontend State & Components**:
   - `frontend/src/components/PatentCard.jsx`: Verified card with badges and score meters. We will add selection checkbox props (`selectable`, `selected`, `onToggleSelect`) without altering existing layout.
   - `frontend/src/pages/Results.jsx`: Search results page. We will add selection state (max 3, min 2) with a floating "Compare Selected (X)" action bar.
   - `frontend/src/App.jsx`: Main navigation and layout router. We will add `compare` to `navItems` and route `<PatentComparison />`.

---

## 3. Files to Be Created

1. `backend/comparison/__init__.py`: Module exports.
2. `backend/comparison/models.py`:
   - `CompareRequest`: accepts `patents: Optional[List[Dict[str, Any]]]`, `patent_ids: Optional[List[str]]`, `session_id: Optional[str]`.
   - `DeepDiveRequest`: accepts `patent: Optional[Dict[str, Any]]`, `patent_id: Optional[str]`, `comparison_context: Optional[List[Dict[str, Any]]]`.
   - `PatentComparisonMatrixRow`, `PatentComparisonResponse`, `DeepDiveResponse`.
3. `backend/comparison/engine.py`:
   - `PatentComparisonEngine`:
     - Validates selection (min 2, max 3 patents).
     - Resolves patent objects from request or session/Chroma.
     - Performs structured comparison synthesis (core invention, technical approach, shared concepts, distinct concepts, key differences).
     - Reuses `detect_innovation_gaps` for combination gaps.
     - Calculates analytical technical similarity matrix.
     - Performs Deep-Dive analysis for individual patents.
     - Provides deterministic fallback if LLM is unavailable or quota-limited.
4. `backend/api/routes/compare.py`:
   - `POST /api/compare`: Executes 2-3 patent comparison.
   - `POST /api/compare/deep-dive`: Executes single patent deep dive.
5. `frontend/src/pages/PatentComparison.jsx`:
   - Comparison workspace page:
     - Header & patent selection selector / switcher.
     - Selected patent summary cards (using `PatentCard`).
     - AI Comparison Summary & Similarity Matrix.
     - Comparison Matrix Table (Core invention, Problem, Solution, Inputs, Pipeline, AI/ML, Output, Applicant, Date).
     - Shared Concepts pills & Distinct Concepts list.
     - Key Technical Differences explanation cards.
     - Potential Combination Gaps section.
     - Interactive Deep Dive drawer/modal for any selected patent.
6. `backend/tests/test_feature2_comparison.py`:
   - 20 comprehensive unit and integration tests.
7. `docs/feature-2-comparison-implementation-plan.md` (this plan).
8. `docs/feature-2-comparison.md`: Feature guide and API documentation.
9. `docs/feature-2-comparison-implementation-report.md`: Verification and regression report.

---

## 4. Files to Be Modified

1. `backend/api/main.py`: Mount `compare.router` under `/api`.
2. `backend/copilot/service.py`: Wire `CopilotService._handle_compare` to use `PatentComparisonEngine`.
3. `frontend/src/components/PatentCard.jsx`: Add optional selection support (`selectable`, `selected`, `onToggleSelect`, `onDeepDive`).
4. `frontend/src/pages/Results.jsx`: Add patent selection state and floating "Compare Selected" action bar.
5. `frontend/src/services/api.js`: Add `comparePatents({ patents, patentIds, sessionId })` and `getPatentDeepDive({ patent, patentId, comparisonContext })`.
6. `frontend/src/App.jsx`: Add `compare` tab to `navItems`, maintain `comparisonPatents` state across navigation.

---

## 5. Technical Comparison & Grounding Strategy

1. **Selection Rules**:
   - Minimum 2 patents required. If < 2: return clear validation error `"Select at least 2 patents to compare."`
   - Maximum 3 patents supported. If > 3: return validation error `"Comparison is limited to 3 patents."`
2. **Comparison Matrix Dimensions**:
   - Core invention
   - Problem addressed
   - Technical approach
   - Input / data sources
   - Processing pipeline
   - AI / ML methods (e.g. CNN, Transformer, SVM; strictly extracted only when present in evidence)
   - Key components
   - Output
   - Shared concepts
   - Distinct concepts within comparison set
   - Applicant & publication date
3. **Evidence Indicators**:
   - Each dimension row indicates primary source: `Abstract`, `Claims`, `Description`, or `Metadata`.
4. **Anti-Hallucination & Legal Safeguards**:
   - System instruction forbids inventing facts or methods not in patent evidence.
   - For missing evidence: explicitly renders `"Not available in retrieved evidence."`
   - Legal disclaimers: strictly analytical, no infringement/patentability conclusions.

---

## 6. Testing & Regression Strategy

1. **Unit & Integration Suite (`backend/tests/test_feature2_comparison.py`)**:
   - Test 1: 2-patent comparison execution
   - Test 2: 3-patent comparison execution
   - Test 3: >3 patents rejection (400 validation error)
   - Test 4: <2 patents rejection (400 validation error)
   - Test 5: Invalid patent ID handling
   - Test 6: Comparison API schema response validation
   - Test 7: Core invention extraction correctness
   - Test 8: Technical approach comparison correctness
   - Test 9: Shared concept extraction
   - Test 10: Distinct concept extraction
   - Test 11: Combination-gap reuse from Phase 6A.1
   - Test 12: Missing evidence handling ("Not available in retrieved evidence")
   - Test 13: Anti-hallucination check for unmentioned ML methods
   - Test 14: Claim focus handling without legal construction
   - Test 15: Source provenance preservation (`LOCAL`, `EPO LIVE`)
   - Test 16: Partial retrieval graceful handling
   - Test 17: LLM quota / timeout deterministic fallback
   - Test 18: Copilot integration with comparison engine
   - Test 19: PatentCard selection prop compatibility
   - Test 20: Deep dive endpoint response validation
2. **Regression Suite**:
   - All 66 existing tests must continue passing (Phase 6A.1, Phase 6B, Phase 6A retrieval, Feature 1 Copilot).
   - Frontend Vite build must pass cleanly.
