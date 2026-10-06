# PatentIQ 🧠⚖️
### AI-Powered Natural Language Patent Search, Prior-Art Discovery & Novelty Intelligence

PatentIQ is a production-grade enterprise patent intelligence platform. It combines a local hybrid vector and lexical store of **115,625 Indian Patent Office (IPO) records** with **live on-demand federated knowledge expansion** via the **European Patent Office (EPO) European Publication Server (EPS)** REST API v1.2.

---

## 🚀 Key Features

* **Natural Language Invention Planning**: Translates researcher questions and invention summaries into structured Boolean phrases, candidate IPC/CPC classifications, and key technical concepts.
* **Dual-Track Hybrid Retrieval**:
  * **Dense Semantic Search**: `all-MiniLM-L6-v2` dense vector embeddings indexed in ChromaDB.
  * **Lexical / BM25 Search**: Precision token matching across titles, abstracts, and claims.
  * **Reciprocal Rank Fusion**: Min-Max normalized hybrid score calibration.
* **Federated Knowledge Expansion (Phase 6B)**:
  * On-demand live enrichment from the official **EPO European Publication Server (EPS)**.
  * Safe `ep-patent-document` XML parsing (XXE protected).
  * Sliding 7-day fair-use bandwidth tracking with a 90% safety threshold (4.5 GB cutoff).
  * Local document caching and automatic non-blocking local fallback if the external server is unavailable.
* **Concept Coverage & Whitespace Intelligence**:
  * 5-band concept coverage scoring (80–100% Strongly Represented down to 0% No Meaningful Evidence).
  * Distinguishes exact phrase absence from semantic concept presence.
  * Multi-concept combination gap detection (`[COMBO]`).
* **Canonical AI-Estimated Novelty Indicator**:
  * Single canonical score contract across summary metrics, circular gauge dials, and detailed reports.
  * Statutory disclaimers preventing misleading legal determinations.
* **Explainable Re-Ranking**:
  * Explainable ranking reasons attached to every retrieved patent candidate.
* **Modern Interactive Dashboard**:
  * React + Vite SPA with real-time analytics, SVG gauges, and source provenance badges (`LOCAL`, `EPO LIVE`, `LOCAL + EPO`).

---

## 🏗️ Architecture

```
                               USER QUERY
                                   │
                                   ▼
                         QUERY UNDERSTANDING
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
            LOCAL PATENT SOURCE           EPO PUBLICATION SOURCE
         (115,625-patent ChromaDB)         (Live EPO EPS v1.2)
                    │                             │
                    └──────────────┬──────────────┘
                                   ▼
                             RESULT FUSION
                       (Deduplication + Calibration)
                                   │
                                   ▼
                          EXISTING RE-RANKING
                                   │
                                   ▼
                        CONCEPT COVERAGE SCORING
                                   │
                                   ▼
                      AI NOVELTY & WHITESPACE ENGINE
                                   │
                                   ▼
                          GEMINI RAG / REPORT
```

---

## 🛠️ Tech Stack

* **Backend**: FastAPI, Python 3.12, Uvicorn, Pydantic v2
* **Vector Store**: ChromaDB (115,625 documents)
* **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
* **LLM Engine**: Google Gemini API (`gemini-2.5-flash`) with deterministic fallback
* **External Live Source**: European Patent Office (EPO) European Publication Server (EPS v1.2)
* **Frontend**: React 18, Vite, Lucide Icons

---

## 🚦 Quickstart

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/Ashritha1906/PatentIQ.git
cd PatentIQ

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env with:
# GEMINI_API_KEY=your_gemini_api_key
# EPO_ENABLED=true

# Launch the FastAPI server
uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Testing

```bash
# Run Phase 6B Federated Retrieval Tests (11 tests)
python -m unittest backend/tests/test_phase6b_federated_retrieval.py

# Run Phase 6A.1 Corrections Tests (14 tests)
python -m unittest backend/tests/test_phase6a1_corrections.py

# Run Phase 6A Retrieval Regression Tests (21 tests)
python -m unittest backend/tests/test_phase6a_retrieval.py

# Run Core API Tests (8 tests)
python -u backend/tests/api_tests/test_api.py
```

---

## ⚖️ Disclaimer

*PatentIQ is an automated prior-art similarity indicator and is not a legal determination of patentability, novelty, or non-infringement.*
