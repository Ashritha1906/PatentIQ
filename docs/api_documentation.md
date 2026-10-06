# PatentIQ REST API Documentation (Phase 5)

This document provides technical reference for integrating with the PatentIQ backend services.

## Base URL
All API endpoints are prefixed with `/api`.
- Local host URL: `http://127.0.0.1:8000/api`

---

## Endpoints Overview

| Method | Endpoint | Description | Payload Type | Response Type |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/health` | Verify database, environment and LLM client status. | None | JSON |
| **POST** | `/search` | Retrieve raw list of semantically similar patents. | `IdeaRequest` | `List[Patent]` |
| **POST** | `/novelty` | Calculate and return only the novelty score details. | `IdeaRequest` | `NoveltyScore` |
| **POST** | `/analyze` | Execute the complete PatentIQ RAG analytical pipeline. | `IdeaRequest` | `PatentIQResponse` |

---

## Endpoint Details

### 1. System Health Status
- **URL:** `/health`
- **Method:** `GET`
- **Headers:** None
- **Response Structure (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected (count: 10450)",
  "llm_mode": "live",
  "environment": {
    "db_path_exists": true
  }
}
```

### 2. Semantic Prior Art Search
- **URL:** `/search`
- **Method:** `POST`
- **Request Headers:** `Content-Type: application/json`
- **Request Payload (`IdeaRequest`):**
```json
{
  "idea_text": "Non-invasive wearable blood glucose sensor using optical absorption",
  "top_k": 3,
  "domain_filter": "BIO-MEDICAL ENGINEERING",
  "applicant_filter": "Medtronic"
}
```
- **Response Structure (200 OK):** Returns a list of matching patent records.
```json
[
  {
    "application_number": "101/CHE/2012",
    "title": "OPTICAL SPECTROSCOPIC GLUCOSE MONITOR",
    "similarity_score": 0.8145,
    "distance": 0.1855,
    "field_of_invention": "BIO-MEDICAL ENGINEERING",
    "classification_ipc": "A61B 5/145",
    "applicant_name": "Medtronic Inc",
    "patent_text": "A wearable wristband utilizing optical sensors..."
  }
]
```

### 3. Novelty Evaluation
- **URL:** `/novelty`
- **Method:** `POST`
- **Request Payload (`IdeaRequest`):** Same as `/search`
- **Response Structure (200 OK):**
```json
{
  "novelty_score": 78,
  "band": "Potentially Distinct",
  "explanation": "The AI-estimated Novelty Score is 78/100... Key Contributing Factors...",
  "breakdown": {
    "similarity_overlap": 18.55,
    "concept_uniqueness": 85.0,
    "domain_saturation": 20.0
  }
}
```

### 4. Full Analytical Intelligence Report
- **URL:** `/analyze`
- **Method:** `POST`
- **Request Payload (`IdeaRequest`):** Same as `/search`
- **Response Structure (200 OK - `PatentIQResponse`):**
```json
{
  "user_idea": "Non-invasive wearable blood glucose sensor...",
  "technology_domain": {
    "primary_domain": "Healthcare",
    "key_concepts": ["optical sensing", "glucose monitor"],
    "keywords": ["sensor", "glucose", "optical"]
  },
  "similar_patents": [ ... ],
  "evidence_ranking": [
    {
      "application_number": "101/CHE/2012",
      "title": "OPTICAL SPECTROSCOPIC GLUCOSE MONITOR",
      "applicant_name": "Medtronic Inc",
      "field_of_invention": "BIO-MEDICAL ENGINEERING",
      "classification_ipc": "A61B 5/145",
      "evidence_score": 88.5,
      "scoring_breakdown": {
        "semantic": 81.45,
        "concept_coverage": 90.0,
        "domain_alignment": 100.0,
        "metadata_relevance": 95.0
      }
    }
  ],
  "concept_clusters": {
    "concept_map": "[Cluster 1: Optoelectronics] - [101/CHE/2012]\n[Cluster 2: Biosensing] - [202/CHE/2013]",
    "cluster_summary": "Retrieved patents cluster into optical diagnostics and biosensing hardware."
  },
  "novelty_score": { ... },
  "innovation_gaps": [
    {
      "concept": "Wearable Continuous Wristband Tracking",
      "representation_status": "weakly-represented",
      "explanation": "Prior art focuses on benchtop spectroscopy rather than continuous wearable integration."
    }
  ],
  "analysis": "### 1. Similar Technologies\nRetrieved patent [101/CHE/2012] details optical sensing but...",
  "confidence_score": {
    "rating": "HIGH",
    "score": 82.5,
    "explanation": "Confidence Rating: HIGH (82.5%). Explanation: The retrieved evidence is highly relevant..."
  }
}
```

---

## Error Codes & Validation Filters

- **400 Bad Request:** Occurs if filters are invalid, or if the vector database contains zero records.
- **422 Unprocessable Entity:** Standard FastAPI input validation error (e.g. missing `idea_text` field in request body).
- **500 Internal Server Error:** Pipeline execution failure (e.g., database timeout or LLM quota limits exceeded).
```json
{
  "detail": "Pipeline execution failed: [Details of error]"
}
```
