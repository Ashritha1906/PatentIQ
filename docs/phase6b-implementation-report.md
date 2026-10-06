# PatentIQ — Phase 6B Implementation & Federated Retrieval Report

**Status:** COMPLETE & PRODUCTION-READY  
**Date:** 2026-10-06  
**Scope:** Live Patent Knowledge Expansion via European Publication Server (EPS REST API v1.2), Provider Abstraction Layer, Safe XML Parsing, Result Fusion, Fair-Use Bandwidth Tracking, and Provenance Preservation.

---

## 1. Phase 6B Status
Phase 6B is **100% complete**. The live European Patent Office (EPO) European Publication Server (EPS) has been integrated as an additive on-demand enrichment source without mutating the local 115,625-record Indian Patent Office (IPO) ChromaDB vector store or disturbing existing Phase 6A intelligence algorithms.

---

## 2. Files Created
1. `backend/patent_sources/__init__.py`: Package export interface for provider architecture.
2. `backend/patent_sources/config.py`: Configuration models and settings (`EPO_ENABLED`, `EPO_BASE_URL`, `EPO_USAGE_LIMIT_BYTES`, `EPO_SAFETY_THRESHOLD`, `SOURCE_MODE`).
3. `backend/patent_sources/base.py`: Abstract Base Class `PatentSource` defining the provider contract.
4. `backend/patent_sources/local_source.py`: `LocalPatentSource` wrapping the local ChromaDB and BM25 index.
5. `backend/patent_sources/epo_usage_tracker.py`: Thread-safe sliding 7-day fair-use bandwidth monitor with 90% (4.5 GB) safety cutoff.
6. `backend/patent_sources/epo_cache.py`: Local document caching layer based on normalized publication IDs.
7. `backend/patent_sources/epo_xml_parser.py`: Safe `ep-patent-document` XML parser guarding against XXE.
8. `backend/patent_sources/epo_client.py`: HTTP client for official EPO EPS REST API v1.2 with timeouts and exponential backoff.
9. `backend/patent_sources/epo_publication_source.py`: `EPOPublicationSource` implementation.
10. `backend/patent_sources/fusion.py`: `ResultFusion` cross-source deduplication, provenance tracking, and score calibration.
11. `backend/tests/test_phase6b_federated_retrieval.py`: Comprehensive test suite with 11 isolated unit tests.
12. `backend/evaluation/phase6b_controlled_live_test.py`: Live integration benchmark script against official EPO servers.
13. `docs/phase6b-implementation-report.md`: Master architectural report.

---

## 3. Files Modified
1. `backend/retrieval/identifier_normalizer.py`: Fixed kind_code logic so unprovided codes strictly return `None` (never inferred as `"A"`); eliminated synthetic date fabrication.
2. `backend/retrieval/query_model.py`: Added `source_mode` and `provenance_metadata` to `NLSearchRequest` and `NLSearchResponse`; updated defaults.
3. `backend/retrieval/nl_retrieval.py`: Removed hardcoded kind_code defaulting in candidate mapping.
4. `backend/api/services/orchestrator.py`: Integrated federated search and result fusion into `search_natural_language()`.
5. `backend/api/routes/search.py`: Propagated `source_mode` parameter into orchestration service.
6. `frontend/src/components/PatentCard.jsx`: Added provenance badges (`LOCAL`, `EPO LIVE`, `LOCAL + EPO`).
7. `backend/tests/test_phase6a1_corrections.py`: Updated assertions for kind code and publication date safety.

---

## 4. Architecture Changes
The system now adheres to a clean, decoupled 5-tier architecture:

```
DATA SOURCES (Local ChromaDB + Live EPO EPS v1.2)
       ↓
PROVIDER ABSTRACTION LAYER (PatentSource -> LocalPatentSource / EPOPublicationSource)
       ↓
RESULT FUSION & DEDUPLICATION (ResultFusion)
       ↓
INTELLIGENCE LAYER (Novelty Indicator + Whitespace Detection)
       ↓
RAG / PRESENTATION (Gemini Analysis + PatentIQ Dashboard)
```

EPO EPS API calls are strictly encapsulated in `backend/patent_sources/` and never invoked inside novelty, whitespace, or frontend components.

---

## 5. Kind-Code Correction Details
- **Prior Defect**: When the source corpus omitted a publication kind code, the system defaulted to `kind_code = "A"`.
- **Correction**: Verified kind codes (e.g. `"A1"`, `"B2"`) are preserved when explicitly present. When omitted in source data, `kind_code` returns `None` (`null`). It is **never** inferred as `"A"`.
- **Publication Dates**: Dates are strictly preserved when present in source data; synthetic dates (e.g. `"2020-01-01"`) are never fabricated.

---

## 6. EPO Integration Details
- **Service**: European Patent Office (EPO) European Publication Server (EPS).
- **Protocol**: REST API v1.2 (`https://data.epo.org/publication-server/rest/v1.2`).
- **Authentication**: Free, unauthenticated, zero API keys or OAuth required.
- **Fair-Use Limits**: 5 GB per sliding 7-day window per IP address.
- **Safety Cutoff**: Configurable 90% threshold (4.5 GB) halts live calls before external throttling occurs.

---

## 7. XML Fields Successfully Parsed
Validated on official `ep-patent-document-v1-7-1` XML:
- `publication_number`: Normalized `EP` + 7 digits (e.g. `EP4812013`)
- `country`: Canonical `"EP"`
- `kind_code`: Extracted from root attribute or `B130` (e.g. `"A1"`, `"B1"`)
- `publication_date`: Converted from `YYYYMMDD` to ISO `YYYY-MM-DD`
- `title`: Extracted from `B542` (prioritizing English `lang="en"`)
- `abstract`: Extracted from `<abstract lang="en"><p>...</p></abstract>`
- `applicants`: Extracted from `B711/snm`
- `inventors`: Extracted from `B721/snm`
- `ipc`: Extracted from `classification-ipcr/text`
- `cpc`: Extracted from `classification-cpc/text`
- `claims`: Extracted from `<claims>//claim-text`
- `description`: Bounded slice of `<description>//p`

---

## 8. Provider Architecture
Extensible object-oriented abstraction:
- `PatentSource` (Base Class): `search()`, `fetch_document()`, `health_check()`, `get_metadata()`.
- `LocalPatentSource`: Exposes local ChromaDB and BM25 index with source tag `"LOCAL_PATENTIQ"`.
- `EPOPublicationSource`: Exposes live EPS retrieval with source tag `"EPO_EPS"`.
- Designed for future plug-and-play expansion (e.g. `USPTOSource`, `LensSource`).

---

## 9. Local / Live / Hybrid Behavior
- `source_mode="local"`: Runs 100% offline using local ChromaDB (0 network calls).
- `source_mode="live"`: Queries live EPO EPS publications (falls back to local if unavailable).
- `source_mode="hybrid"` (Default): Combines local candidate set with live EPO candidate set via `ResultFusion`.

---

## 10. Cache Behavior
- Local filesystem cache in `data/cache/epo_documents/`.
- Keyed by sanitized publication identifier (`EP4812013.json`).
- Stores document metadata, parsed JSON, byte size, and fetch timestamp.
- Verified: Second fetch of the same publication results in an instantaneous Cache HIT.

---

## 11. Usage Tracking Behavior
- Monitored by `EPOUsageTracker` persisting to `data/cache/epo_usage.json`.
- Maintains sliding 7-day window of transferred bytes and HTTP response codes.
- Automatically computes rolling 7-day consumption against the 5 GB budget.
- Triggers safety throttle when usage reaches 4.5 GB (90%).

---

## 12. Failure & Fallback Behavior
- If EPO EPS is unreachable, times out, returns HTTP 500/404, or exceeds the fair-use threshold:
  - Non-fatal warning is logged.
  - Live retrieval returns `[]`.
  - Result fusion passes local results through unaltered.
  - The pipeline never crashes.
  - `provenance_metadata.live_retrieval_status` reports `"failed: <reason>"`.

---

## 13. API Changes
- Extended `POST /search` and `POST /analyze`:
  - Request field: `source_mode: "local" | "hybrid" | "live"` (optional, defaults to `"hybrid"`).
  - Response metadata: `source_mode`, `provenance_metadata` (including `live_retrieval_used`, `live_retrieval_status`, `local_results_count`, `live_results_count`, `fused_results_count`, `duplicates_merged`).

---

## 14. Frontend Changes
- `PatentCard.jsx`: Renders distinctive provenance badges:
  - `LOCAL` (Default Indian corpus)
  - `EPO LIVE` (Live European publication)
  - `LOCAL + EPO` (Cross-source fused duplicate)
- Zero framework rewrites; completely backward compatible with existing UI.

---

## 15. Tests Added
In `backend/tests/test_phase6b_federated_retrieval.py` (11 new tests):
1. `test_epo_xml_parser_full_document`: Parses complete `ep-patent-document`.
2. `test_epo_xml_parser_missing_fields_never_fabricates_kind_code`: Verifies kind_code and date remain `None`.
3. `test_epo_xml_parser_malformed_xml_handling`: Verifies XML parsing error handling.
4. `test_local_patent_source_properties_and_metadata`: Verifies `LocalPatentSource`.
5. `test_local_patent_source_search_tags_provenance`: Verifies local provenance tagging.
6. `test_epo_usage_tracker_sliding_window_and_safety_cutoff`: Tests 90% cutoff behavior.
7. `test_epo_client_skips_when_throttled`: Verifies network avoidance when over budget.
8. `test_epo_cache_hit_and_miss_lifecycle`: Verifies cache hit/miss persistence.
9. `test_result_fusion_deduplication_and_provenance_merging`: Tests deduplication and merged provenance.
10. `test_epo_failure_falls_back_cleanly_to_local_results`: Tests timeout fallback to local results.
11. `test_api_source_modes`: Verifies `source_mode="local"` avoids EPO calls.

---

## 16. Existing Tests Passed
- `test_phase6a1_corrections.py`: **14 / 14 PASS** (0.012s)
- `test_phase6a_retrieval.py`: **21 / 21 PASS** (11.121s)
- `test_api.py`: **8 / 8 PASS** (0.48s)
- `test_phase6b_federated_retrieval.py`: **11 / 11 PASS** (6.378s)
- Frontend build: **Vite build clean in 1.07s (0 errors)**

---

## 17. Live EPO Integration Result
- Successfully connected to `https://data.epo.org/publication-server/rest/v1.2`.
- Fetched live document `EP4812013NWA1` (`13,674` bytes) in `454.7ms`.
- Parsed into canonical PatentIQ schema in `0.81ms`.
- Stored and verified in local cache with subsequent Cache HIT.
- Executed federated hybrid search on real-world diabetic retinopathy query with local fallback verified in `136.5ms`.

---

## 18. Performance Measurements
- **Local Retrieval Latency**: 120 – 150 ms (pure ChromaDB + BM25)
- **Live EPO HTTP Fetch**: 350 – 550 ms per document
- **EPO XML Parsing**: < 1.0 ms per document
- **Result Fusion & Deduplication**: < 0.2 ms
- **Offline / Local Mode Overhead**: 0.0 ms

---

## 19. Known Limitations
1. **Jurisdiction Scope**: EPO European Publication Server covers European patent publications (A and B publications). It does not provide global USPTO, JPO, or WIPO patent coverage.
2. **Weekly Publication Batches**: EPS is updated weekly; it serves publication files rather than an open Boolean keyword search engine.

---

## 20. Recommended Next Phase
- **Phase 7A**: Advanced USPTO bulk ingestion & federated patent search.
- **Phase 7B**: Multi-jurisdiction visual citation graphing and family linking.
