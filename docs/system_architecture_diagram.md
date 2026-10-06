# PatentIQ System Architecture (Phase 5)

The following Mermaid diagram visualizes the request lifecycle, data flow, and components of the PatentIQ platform.

```mermaid
graph TD
    %% Clients & API Entry
    User([User Client Browser])
    UI[HTML5/CSS3 Single-Page App]
    API[FastAPI Gateway: backend/api/main.py]
    
    User <-->|HTTP / CORS| UI
    UI <-->|POST /api/analyze| API
    UI -->|GET /api/health| API
    
    %% Service Layer
    Orch[Orchestrator: PatentIntelligenceService]
    API <-->|Orchestrates Pipeline| Orch
    
    %% External AI Models & DB Abstraction
    QU[LLM Query Understanding]
    VS[VectorStore Interface]
    Chroma[ChromaVectorStore]
    ChromaDB[(ChromaDB Index)]
    ST[SentenceTransformers: all-MiniLM-L6-v2]
    Gemini[Gemini 2.5 LLM Engine]
    
    Orch -->|1. Extract Concepts| QU
    Orch -->|2. Search Prior Art| VS
    VS -.->|Abstracts| Chroma
    Chroma -->|Encode Text| ST
    Chroma -->|Query| ChromaDB
    ChromaDB -->|Retrieved Patents| Chroma
    Chroma -->|Patents List| VS
    VS -->|Unique Patents| Orch
    
    %% Analytics Pipeline
    Rank[Evidence Ranker]
    Cluster[Concept Clustering]
    Novelty[Novelty Scorer]
    Gaps[Whitespace Gap Detector]
    Compress[Context Compressor]
    Confidence[Confidence Assessor]
    
    Orch -->|3. Rank Metadata| Rank
    Orch -->|4. Unsupervised Map| Cluster
    Orch -->|5. Programmatic Score| Novelty
    Orch -->|6. Whitespace Identify| Gaps
    Orch -->|7. prompt Budgeting| Compress
    Orch -->|8. Evidence Averages| Confidence
    
    %% AI Generation
    Compress -->|Context Block| Gemini
    Orch -->|9. Comparative Analysis| Gemini
    Gemini -->|AI Markdown Report| Orch
    
    %% Response compiled
    Orch -->|10. Aggregate Dictionary| API
    API -->|Validates Pydantic Schema| UI
```

## Request Flow Lifecycle

1. **Query Entry:** The user inputs an invention description into the frontend SPA.
2. **Query Understanding:** The FastAPI backend receives the request and forwards it to the Orchestrator, which utilizes the Gemini client to parse the core problem, isolate keywords, and identify the primary technology domain.
3. **Database Retrieval:** Using the optimized query, the `ChromaVectorStore` encodes the text using SentenceTransformers and queries ChromaDB. Filters are merged during search.
4. **Programmatic Analysis:**
   - The retrieved patents are deduplicated.
   - The `EvidenceRanker` scores the alignment of patents against search variables.
   - The `ConceptClustering` generates ASCII cluster landscapes.
   - The `NoveltyScorer` evaluates similarity overlap, concept uniqueness, and domain saturation.
   - The `GapDetector` highlights unrepresented technical elements.
5. **Generative RAG Synthesis:** The compressed patent details and user idea are submitted to Gemini to generate the 6-part Comparative Novelty report.
6. **Confidence Scoring:** Overall evidence ratings are programmatically calculated.
7. **Response Delivery:** The compiled dictionary is validated by FastAPI against the `PatentIQResponse` Pydantic model and returned to the client browser to render.
