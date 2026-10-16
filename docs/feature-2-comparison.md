# PatentIQ — Feature 2: Patent Comparison & Deep-Dive Workspace

## 1. Feature Overview
The **Patent Comparison & Deep-Dive Workspace** empowers researchers and IP engineers to perform structured, evidence-grounded technical comparisons across 2 to 3 patent documents. Built directly upon PatentIQ's existing retrieval and RAG intelligence architecture, the workspace answers fundamental technical research questions:
- What does each patent actually do?
- What technical approach does each patent use?
- What concepts and technical methodologies do they share?
- What architectural or algorithmic dimensions are distinct within the selected set?
- What potential technology combination gaps exist between their approaches?
- What key research questions should be investigated next?

> **Legal Guardrail Notice**:
> This feature provides **automated research intelligence**. It is strictly an analytical aid and does **NOT** constitute legal claim construction, freedom-to-operate analysis, patent validity verification, or a legal non-infringement determination.

---

## 2. User Workflow

```
[ Natural Language Search / Idea Analysis ]
                     ↓
        [ Prior Art Patent Cards ]
                     ↓
[ Select 2–3 Patents via Interactive Checkbox ]
                     ↓
      [ "Compare Selected (X/3) →" ]
                     ↓
[ Patent Comparison & Deep-Dive Workspace ]
  ├── Compact Patent Metadata Cards + Provenance
  ├── AI Grounded Comparison Summary (Gemini / Fallback)
  ├── AI-Estimated Technical Similarity Percentage
  ├── Multi-Dimensional Comparison Matrix (11 Technical Dimensions)
  ├── Shared Technical Concepts
  ├── Distinct Technical Concepts ("Distinct within selected set")
  ├── Key Technical Differences
  └── Potential Technology Combination Gaps (Phase 6A.1 reuse)
                     ↓
[ Click "Deep Dive 🔍" on any Patent ]
  └── In-Depth System Workflow, Methods, Concepts & Research Questions
```

---

## 3. Architecture & Engine Reuse

Feature 2 strictly conforms to the **Zero Duplication** rule:
- **No separate RAG engine**: Reuses PatentIQ's centralized LLM client (`backend/llm/gemini_client.py`).
- **No separate vector store**: Relies on ChromaDB (`backend/retrieval/vector_store.py`).
- **No separate embedding model**: Uses the existing all-MiniLM-L6-v2 pipeline.
- **No duplicated whitespace engine**: Reuses `detect_innovation_gaps` from `backend/intelligence/innovation_gap.py` directly for combination gap discovery.
- **Feature 1 Copilot integration**: Feature 1 Copilot directly delegates the `COMPARE` intent to `comparison_engine.compare()`.

---

## 4. Multi-Dimensional Comparison Matrix

The workspace evaluates 11 structured dimensions across the compared documents:

| Dimension | Primary Evidence Source | Description |
|-----------|------------------------|-------------|
| **Core Invention** | Abstract | Core technical solution proposed by the document |
| **Problem Addressed** | Abstract | Specific operational or system bottleneck addressed |
| **Technical Approach** | Abstract / Description | Architectural and algorithmic methodology employed |
| **Input / Data** | Description / Abstract | Ingested data types (sensors, imagery, telemetry, signals) |
| **Processing Pipeline** | Description / Abstract | Step-by-step technical execution flow |
| **AI / ML Methods** | Abstract / Description | Substantiated models only (CNN, transformer, LSTM, etc.) |
| **Key Components** | Description | Core hardware/software modules identified |
| **Output** | Abstract / Description | Resulting signals, classifications, or telemetry |
| **Main Concepts** | Abstract | Key technical vocabulary terms |
| **Applicant** | Metadata | Assignee / patent applicant organization |
| **Publication Date** | Metadata | Official publication date |

*Missing Evidence Policy*: If a field is not supported by retrieved document text, the engine explicitly outputs `"Not available in retrieved evidence."` rather than hallucinating facts.

---

## 5. Concept Logic & Combination Gaps

### Shared Concepts
Concepts co-occurring across 2 or more of the selected patents are surfaced as visual tags (`✓ Concept`).

### Distinct Concepts
Concepts found within patent $A$ that do not appear in the other compared patents are classified as **distinct within the selected comparison set**. Global uniqueness is never claimed.

### Potential Combination Gaps
Reuses Phase 6A.1's `detect_innovation_gaps`. When Patent A embodies concept $X$ and Patent B embodies concept $Y$, but the selected set shows limited joint coverage of $X + Y$, the workspace surfaces:
> *"Within the selected prior-art set, the combination of X and Y appears less represented."*

---

## 6. AI Deep Dive Explorer

Users can explore any individual patent in depth:
1. **Plain-Language Executive Summary**
2. **Problem Addressed**
3. **Proposed Technical Solution**
4. **Step-by-Step System Workflow**
5. **Substantiated Technologies & Methods**
6. **Distinction Within Current Comparison**
7. **Forward-Looking Research Questions**
8. **Claim Focus**: *"The retrieved claim text focuses on: ..."* (or explicitly notes claim absence if claims are missing from the source).

---

## 7. API Specification

### `POST /api/compare`
Request:
```json
{
  "patents": [
    { "publication_number": "IN202011001", "title": "...", "abstract": "..." },
    { "publication_number": "EP3456789", "title": "...", "abstract": "..." }
  ],
  "session_id": "optional-session-id"
}
```
Response:
```json
{
  "patents": [...],
  "summary": "AI comparative synthesis...",
  "matrix": [...],
  "shared_concepts": ["Sensor", "Telemetry"],
  "distinct_concepts": { "IN202011001": ["Drone", "Cnn"], "EP3456789": ["Temporal"] },
  "key_differences": [...],
  "combination_gaps": [...],
  "technical_similarities": [
    { "pair": ["IN202011001", "EP3456789"], "similarity_percentage": 42, "explanation": "..." }
  ],
  "disclaimer": "This comparison provides automated research intelligence and does NOT constitute a legal determination..."
}
```

### `POST /api/compare/deep-dive`
Request:
```json
{
  "patent": { "publication_number": "IN202011001", "title": "...", "abstract": "..." },
  "comparison_context": [...]
}
```
Response:
```json
{
  "patent_id": "IN202011001",
  "title": "...",
  "summary": "...",
  "problem_addressed": "...",
  "proposed_solution": "...",
  "technical_workflow": "Telemetry Ingestion -> Preprocessing -> Algorithmic Processing -> Decision State",
  "technologies_methods": ["Cnn"],
  "important_concepts": [...],
  "distinction_in_set": "Distinct within the selected comparison set primarily through emphasis on Drone, Cnn.",
  "research_questions": [...],
  "claim_focus": "The retrieved claim text focuses on: 1. An aerial monitoring apparatus...",
  "disclaimer": "This deep dive provides automated technical analysis based on available patent text and does NOT constitute legal claim construction..."
}
```

---

## 8. Verification & Test Suite

The feature is validated by 20 unit and integration tests in `backend/tests/test_feature2_comparison.py`:
1. Two-patent selection
2. Three-patent selection
3. More-than-three rejection
4. Fewer-than-two rejection
5. Invalid patent ID handling
6. Comparison API schema validation
7. Core invention extraction
8. Technical approach comparison
9. Shared concept extraction
10. Distinct concept extraction
11. Combination-gap reuse
12. Missing evidence handling
13. Anti-hallucination of ML methods
14. Claim information handling
15. Provenance preservation
16. Partial retrieval handling
17. LLM failure handling
18. Feature 1 Copilot integration
19. PatentCard compatibility
20. Deep Dive response schema & distinction in set

---

## 9. Known Limitations
- Full claim texts are available on EPO live documents and structured Indian patent records; records lacking claim text display the explicit fallback indicator.
- Comparative summaries reflect the retrieved corpus and do not account for unpublished pending applications.