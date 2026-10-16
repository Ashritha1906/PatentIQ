# PatentIQ — Feature 4: Research Intelligence Report Engine

## 1. Overview & Architecture

PatentIQ's **Feature 4: Research Intelligence Report & Export Engine** consolidates multi-dimensional patent intelligence into structured, evidence-grounded research reports. It unifies all prior phases and features:

- **Federated Retrieval (Phase 6B)**: Local PatentIQ Indian patent corpus (~115,625 records) fused with European Publication Server (EPO EPS) live publications.
- **Natural Language Search (Phase 6A)**: Intent-driven query expansion, IPC classification, and hybrid dense-sparse retrieval.
- **Deep-Dive & Comparison Workspace (Feature 2)**: Multi-patent feature matrices, shared technical concepts, distinct concepts, and pairwise combination gaps.
- **Innovation / Idea Refinement Engine (Feature 3)**: Concept coverage representation tiers (Strong, Moderate, Weak, Minimal), whitespace detection, and differentiation pathways.
- **Canonical Novelty Indicator (Phase 6A.1)**: AI-estimated novelty scoring (0-100) and clear non-legal research disclaimers.

---

## 2. Report Schema (13 Structured Sections)

A `ResearchIntelligenceReport` adheres strictly to a 13-section structure defined in `backend/reports/models.py`:

1. **Cover Page & Metadata**: Title, Subtitle, Author, Organization, Report ID, Timestamp, Scope, and Total Patents Reviewed.
2. **Executive Summary**: Synthesized overview of the technology domain, key findings, and research takeaways.
3. **Research Objective & Query Scope**: Formal research objective, search query, IPC classifications, and extracted technical concepts.
4. **Methodology & Sources**: Sources utilized (`LOCAL_PATENTIQ`, `EPO_EPS`), retrieval mode (`HYBRID`), and fusion parameters.
5. **Prior-Art Landscape & Retrieved Patents**: Ranked list of prior art with publication IDs, titles, dates, applicants, relevance scores, and provenance.
6. **Detailed Patent Summaries**: In-depth breakdowns with abstracts, technical approaches, grounded claims summaries, and relevant excerpts.
7. **Cross-Patent Comparison Matrix**: Comparative feature grid, shared concepts, distinct concepts, and combination gaps across selected candidates.
8. **AI-Estimated Novelty Indicator**: Canonical 0-100 score, assessment band, similarities, differentiation aspects, and mandatory non-legal disclaimer.
9. **Concept Coverage & Representation**: Multi-tier breakdown (Strong, Moderate, Weak, Minimal) with supporting excerpts.
10. **Whitespace & Combination Gaps**: Missing combinations and technical whitespace identified across the prior-art landscape.
11. **Technical Differentiation Pathways**: Concrete engineering and architectural directions for researchers.
12. **Applicant & Technology Trends**: Top applicants, publication timeline trends, and IPC distribution.
13. **Limitations & Disclaimer**: Explicit scope boundaries, database coverage constraints, and formal non-legal research disclaimer.

---

## 3. Export Capabilities

### 3.1 Markdown Export (`backend/reports/markdown_exporter.py`)
- Standard GitHub-flavored markdown with clean navigation links and a full Table of Contents.
- Pre-formatted Markdown tables for comparison matrices, concept coverage, and patent listings.
- Callout blockquotes for novelty indicators and limitations disclaimers.

### 3.2 PDF Export (`backend/reports/pdf_exporter.py`)
- Rendered via **ReportLab** (`SimpleDocTemplate`) with dark/slate typography matching the PatentIQ theme.
- **Two-Pass Numbered Canvas**: Dynamically calculates and renders "Page X of Y" in the running footer.
- **Running Headers**: Clean running header with report title and subtle divider line.
- **Auto-Wrapped Table Cells**: All table contents wrapped inside ReportLab `Paragraph` elements to prevent cell text clipping across page boundaries.
- **Page Breaks**: Logical page flow keeping major sections organized.

---

## 4. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/reports/generate` | Generates a complete 13-section report from search query, innovation context, or patent IDs |
| `GET` | `/api/reports/{report_id}` | Retrieves a previously generated or cached report by ID |
| `GET` | `/api/reports/{report_id}/markdown` | Downloads the report formatted as a `.md` markdown file |
| `GET` | `/api/reports/{report_id}/pdf` | Streams the report formatted as a publication-ready `.pdf` file |

---

## 5. UI Integration

- **Route / Tab**: Mounted under `frontend/src/pages/ReportWorkspace.jsx`, accessible via the **📋 Intelligence Reports** tab in `frontend/src/App.jsx`.
- **Modes**:
  1. *Natural Language Query Mode*: Generates landscape and novelty reports directly from a user's research topic.
  2. *Innovation Context Mode*: Incorporates existing Feature 3 innovation analyses, concept coverage, and whitespace.
  3. *Patent Selection Mode*: Synthesizes reports around specific patents chosen from prior search results.
- **Presets**: Includes one-click presets for rapid testing (Retinal Fundus Imaging, Solid-State Batteries, Drone Collision Avoidance).
- **Actions**: Live multi-section preview with accordion toggles, direct Markdown download, and direct PDF download.

---

## 6. Testing & Quality Assurance

- **Unit & Integration Suite**: `backend/tests/test_feature4_report.py` (26 tests, 100% PASS).
- **Full System Regression Suite**:
  - Feature 4: 26/26 PASS
  - Feature 3 (Innovation): 20/20 PASS
  - Feature 2 (Comparison): 20/20 PASS
  - Feature 1 (Copilot): 20/20 PASS
  - Phase 6A.1 (Corrections): 14/14 PASS
  - Phase 6B (Federated Retrieval): 11/11 PASS
  - Phase 6A (Retrieval): 21/21 PASS
  - **Total: 132/132 PASS across the repository**.
