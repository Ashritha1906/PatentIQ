# Lens Patent API Integration

This document outlines the API specifications and query templates used to connect with Lens.org.

## Connection Endpoint

- **Method:** `POST`
- **URL:** `https://api.lens.org/patent/search`
- **Content-Type:** `application/json`
- **Authorization Header:** `Authorization: Bearer <LENS_API_KEY>`

---

## Query DSL Specifications

The API expects Elasticsearch-style JSON payloads.

### 1. Keyword Search
Matches query terms across title, abstract, and claims:
```json
{
  "query": {
    "query_string": {
      "query": "LiDAR AND sensor"
    }
  },
  "size": 10,
  "from": 0
}
```

### 2. Publication Date Range
Filters documents based on YYYY-MM-DD ranges:
```json
{
  "query": {
    "range": {
      "date_published": {
        "gte": "2024-01-01",
        "lte": "2024-12-31"
      }
    }
  },
  "size": 10,
  "from": 0
}
```

### 3. Assignee / Applicant Search
Matches applicant names (case-insensitive):
```json
{
  "query": {
    "match": {
      "biblio.applicants.extracted_name.value": "Samsung"
    }
  },
  "size": 10
}
```

---

## Throttling & Throttling Mitigation (HTTP 429)

To prevent query exhaustion under low tier plans, our client (`lens_client.py`) automatically intercepts HTTP 429 responses. 
- Retries: **5**
- Backoff Factor: **2.0**
- Timeout: **30 seconds**

On throttling, the system sleeps for `backoff * 2.0` seconds and resubmits the exact same payload context. If the throttling continues after 5 retries, the job raises `LensRateLimitError`.
