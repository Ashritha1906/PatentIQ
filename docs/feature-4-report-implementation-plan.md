# PatentIQ — Feature 4 Implementation Plan
## Research Intelligence Report & PDF / Markdown Export

### 1. Objective
Feature 4 builds a professional Research Intelligence Report & Export engine that consolidates the findings of PatentIQ patent research (search results, patent comparisons, innovation refinement, concept coverage, whitespace, and AI-Estimated Novelty Indicator) into an evidence-grounded, multi-page document exportable as PDF and Markdown.

### 2. Frozen Systems to Reuse (Zero Duplication)
- **Natural Language Search / Federated Retrieval**: `PatentIntelligenceService.search_natural_language()`
- **Concept Extraction**: `PatentIntelligenceService.interpret_query()`
- **AI-Estimated Novelty Indicator**: `backend.intelligence.novelty_scoring.calculate_novelty_score()`
- **Semantic Concept Coverage**: `backend.intelligence.concept_coverage.calculate_concept_coverage()`
- **Combination Gaps & Whitespace**: `backend.intelligence.innovation_gap.detect_innovation_gaps()`
- **Feature 1 Copilot Context**: Session history and intent resolution
- **Feature 2 Comparison**: `PatentComparisonService.compare_patents()`
- **Feature 3 Innovation Refinement**: `InnovationRefinementService.analyze_innovation()`
- **PDF Generation**: `reportlab` (installed and verified in Python 3.12)
- **Markdown Generation**: Pure Python structured Markdown generator

### 3. Report Structure
1. Cover Page (Title, invention topic, date, report ID, confidentiality notice)
2. Executive Summary (Grounded synthesis of findings, top patents, differentiation)
3. Research Objective (User's technical statement)
4. Methodology & Scope (Retrieval mode, databases searched, scoring criteria)
5. Prior-Art Landscape (Summary table with publication IDs, titles, applicants, dates, provenance)
6. Detailed Patent Summaries (Technical approach, problem solved, relevance)
7. Patent Comparison (Multi-patent comparison matrix when available)
8. AI-Estimated Novelty Indicator (Score, band, rationale, disclaimer)
9. Concept Coverage Landscape (5 representation bands)
10. Innovation Whitespace & Combination Gaps (Pairwise under-representation)
11. Potential Differentiation Directions (Feature 3 recommendations & research questions)
12. Key Applicants & Field Distribution (Data-grounded distribution)
13. Limitations & Data Coverage (Corpus boundaries)
14. Mandatory Legal Disclaimer

### 4. Backend API Design
- `POST /api/reports/generate` -> Generates structured report
- `GET /api/reports/{report_id}` -> Returns stored report JSON
- `GET /api/reports/{report_id}/markdown` -> Downloads Markdown file
- `GET /api/reports/{report_id}/pdf` -> Downloads PDF file

### 5. Frontend Architecture
- Page: `frontend/src/pages/ReportWorkspace.jsx`
- Navigation item: `📋 Intelligence Reports`
- Features: Setup form, honest progress state, tabbed/scrollable preview, one-click PDF & Markdown downloads.

### 6. Test & Verification Plan
- 26 tests in `backend/tests/test_feature4_report.py`.
- Regression check on Phase 6A, 6A.1, 6B, Feature 1, Feature 2, Feature 3.
- Frontend production build check.
