# PatentIQ — Feature 3 Implementation Plan
## Innovation / Idea Refinement & Differentiation Engine

### 1. Executive Summary
Feature 3 transforms PatentIQ from a prior-art search and retrieval engine into an **actionable innovation research and differentiation tool**. It analyzes a user's idea against retrieved prior art, measures semantic representation across concepts, reuses existing combination-gap intelligence, and surfaces structured technical differentiation directions and research questions without claiming legal novelty or patentability.

---

### 2. Existing Intelligence Reused (Zero Duplication)
Feature 3 strictly avoids building redundant AI, retrieval, or scoring systems:
- **Retrieval Engine**: Reuses `PatentIntelligenceService._retrieve_context()` and `VectorStore.search()` with ChromaDB and `all-MiniLM-L6-v2`.
- **Query Understanding**: Reuses `understand_query()` (`backend/llm/query_understanding.py`) for domain, keyword, and concept extraction.
- **Novelty Scoring**: Reuses `calculate_novelty_score()` (`backend/intelligence/novelty_scoring.py`) to provide the canonical AI-Estimated Novelty Indicator.
- **Concept Coverage**: Reuses `score_concept_coverage()` and `get_coverage_band()` (`backend/intelligence/innovation_gap.py`) with existing thresholds (Strongly, Moderately, Weakly, Minimally, No Meaningful Evidence).
- **Combination Gaps**: Reuses `detect_innovation_gaps()` (`backend/intelligence/innovation_gap.py`) to identify unrepresented concept pairs.
- **LLM Client**: Reuses `generate_text()` (`backend/llm/gemini_client.py`) with deterministic analytical fallback.
- **Feature 1 Copilot**: Integrated so copilot can handle differentiation queries (`"How can I differentiate my idea?"`).
- **Feature 2 Comparison**: Reuses structured comparison output when available as comparison context.

---

### 3. Proposed Architecture
```
                         User Idea (Natural Language)
                                       ↓
                        InnovationRefinementService
                                       ↓
         ┌─────────────────────────────┴─────────────────────────────┐
         ↓                                                           ↓
   Existing Retrieval                                      Query Understanding
 (ChromaDB + Local/EPO)                                 (Domain & Concept Extraction)
         ↓                                                           ↓
Retrieved Patents Set                                       User Concept List
         └─────────────────────────────┬─────────────────────────────┘
                                       ↓
   ┌───────────────────────────────────┼───────────────────────────────────┐
   ↓                                   ↓                                   ↓
Novelty Indicator              Concept Coverage                    Combination Gaps
(calculate_novelty_score)   (score_concept_coverage)            (detect_innovation_gaps)
   ↓                                   ↓                                   ↓
Canonical Novelty %             5 Coverage Bands                 Identified Gap Pairs
   └───────────────────────────────────┬───────────────────────────────────┘
                                       ↓
                    Grounded Differentiation Synthesizer
                        (LLM + Deterministic Engine)
                                       ↓
        ┌──────────────────────────────┼──────────────────────────────┐
        ↓                              ↓                              ↓
Technical Differentiation      User Idea vs. Prior Art        Actionable Research
       Directions                     Landscape                    Questions
 (Arch, Data, Proc, ML, Comb)   (Represented / Gaps)           (Empirical Experiments)
```

---

### 4. API Design (`POST /api/innovation/analyze`)
**Request**:
```json
{
  "idea": "I am building an AI system that detects diabetic retinopathy...",
  "source_mode": "hybrid",
  "top_k": 5,
  "session_id": "optional",
  "comparison_context": null
}
```
**Response**:
```json
{
  "idea_summary": "...",
  "technology_domain": "...",
  "retrieved_patents": [...],
  "novelty_indicator": { "score": 45, "band": "Some Distinguishing Features", ... },
  "concept_coverage": {
    "strongly_represented": [...],
    "moderately_represented": [...],
    "weakly_represented": [...],
    "minimally_represented": [...],
    "no_meaningful_evidence": [...]
  },
  "idea_vs_prior_art": [
    { "concept": "Deep Learning", "status": "Strongly Represented", "symbol": "✓" },
    { "concept": "Lesion Localization", "status": "Weakly Represented", "symbol": "~" }
  ],
  "combination_gaps": [...],
  "differentiation_directions": [
    {
      "direction_id": "DIR-1",
      "title": "Unified Real-Time Lesion Localization and Severity Grading",
      "category": "Technical Architecture",
      "why_investigate": "Severity grading appears less represented in retrieved prior art...",
      "related_concepts": ["lesion localization", "severity grading"],
      "evidence_gap_level": "HIGHER EVIDENCE GAP",
      "research_questions": ["Can a single-pass backbone localize microaneurysms while predicting global grade?"],
      "related_patent_ids": ["IN202011001", "EP3456789"]
    }
  ],
  "general_research_questions": [...],
  "provenance": { "source": "LOCAL + EPO", ... },
  "disclaimer": "This analysis is based on the retrieved prior-art set and is intended for research purposes. It is not a legal determination of patentability or novelty."
}
```

---

### 5. Frontend Flow & Workspace (`InnovationRefinement.jsx`)
1. **Header**: "Innovation Refinement Workspace" with explicit non-legal guidance alert.
2. **Natural Language Input**: Large multiline textarea with example prompts and sample ideas.
3. **Executive Analysis Summary**: Displays idea summary, number of prior-art records retrieved, provenance badges, and canonical AI-Estimated Novelty Indicator gauge.
4. **Concept Coverage Landscape**: Color-coded cards for the 5 representation bands.
5. **User Idea vs. Prior Art Table**: Direct mapping of user concepts to prior art representation symbols (`✓`, `~`, `—`).
6. **Technical Differentiation Directions**: Categorized cards (Architecture, Data/Input, Processing, AI/ML, System Combination) with why-investigate rationale, related patents, evidence gap levels, and research questions.
7. **Combination Gaps**: Visual representation of joint coverage whitespace.
8. **Relevant Prior Art Carousel / Grid**: Reuses `PatentCard` with selection and deep dive links.

---

### 6. Implementation Steps
1. Create `backend/innovation/models.py` (Pydantic models).
2. Create `backend/innovation/service.py` (Orchestrates retrieval, coverage, novelty, gaps, and differentiation).
3. Create `backend/innovation/__init__.py`.
4. Create `backend/api/routes/innovation.py` and mount in `backend/api/main.py`.
5. Integrate with Feature 1 Copilot (`backend/copilot/service.py`).
6. Create unit and integration tests (`backend/tests/test_feature3_innovation.py`).
7. Update frontend: API client, `InnovationRefinement.jsx`, and `App.jsx` tab navigation.
8. Run full regression test suite (all 106 tests) and verify frontend production build (`vite build`).
9. Write `docs/feature-3-innovation.md` and `docs/feature-3-innovation-implementation-report.md`.