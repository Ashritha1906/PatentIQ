import unittest
import os
import json
import time
from unittest.mock import patch, MagicMock

# Force mock mode for fast deterministic testing
os.environ["MOCK_LLM"] = "true"

from backend.patent_sources.base import PatentSource
from backend.patent_sources.local_source import LocalPatentSource
from backend.patent_sources.epo_publication_source import EPOPublicationSource
from backend.patent_sources.epo_client import EPOClient
from backend.patent_sources.epo_xml_parser import EPOXMLParser
from backend.patent_sources.epo_cache import EPOCache
from backend.patent_sources.epo_usage_tracker import EPOUsageTracker
from backend.patent_sources.fusion import ResultFusion
from backend.patent_sources.config import SOURCES_CONFIG
from backend.retrieval.query_model import PatentSearchResult, PatentQuery

# Representative EPO XML fixture modeled on real ep-patent-document v1.7.1
SAMPLE_EPO_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ep-patent-document country="EP" date-publ="20260930" doc-number="4812013" file="24834062.2" id="EP24834062A1" kind="A1" lang="en">
  <SDOBI lang="en">
    <B100>
      <B110>4812013</B110>
      <B130>A1</B130>
      <B140><date>20260930</date></B140>
      <B190>EP</B190>
    </B100>
    <B500>
      <B540>
        <B542 lang="de">VERFAHREN ZUR HERSTELLUNG VON KARTEN</B542>
        <B542 lang="en">METHOD FOR PRODUCTION OF PRECISION RETINAL MAPS</B542>
        <B542 lang="fr">PROCEDE DE PRODUCTION DE CARTES</B542>
      </B540>
      <B510EP>
        <classification-ipcr sequence="1"><text>G06T  7/00        20060101AFI20260930BHEP</text></classification-ipcr>
        <classification-ipcr sequence="2"><text>A61B  3/12        20060101ALI20260930BHEP</text></classification-ipcr>
      </B510EP>
      <B520EP>
        <classifications-cpc>
          <classification-cpc sequence="1"><text>G06T  7/0012      20130101 FI20260930BHEP</text></classification-cpc>
        </classifications-cpc>
      </B520EP>
    </B500>
    <B700>
      <B710>
        <B711><snm>KITE TECHNOLOGIES GMBH</snm></B711>
        <B711><snm>MEDTECH INNOVATIONS SA</snm></B711>
      </B710>
      <B720>
        <B721><snm>DR. SZABO, Levente</snm></B721>
        <B721><snm>MULLER, Anna</snm></B721>
      </B720>
    </B700>
  </SDOBI>
  <abstract lang="en">
    <p>A computer-implemented method for deep learning based retinal image analysis and severity grading.</p>
  </abstract>
  <description lang="en">
    <p>The present invention relates to computer vision analysis of medical fundus images.</p>
  </description>
  <claims lang="en">
    <claim num="1"><claim-text>A method comprising acquiring a retinal fundus image and computing lesion segmentations.</claim-text></claim>
  </claims>
</ep-patent-document>
"""

# Fixture without kind code and without publication date
SAMPLE_EPO_XML_MISSING_OPTIONAL = """<?xml version="1.0" encoding="UTF-8"?>
<ep-patent-document country="EP" doc-number="4999999">
  <SDOBI lang="en">
    <B100>
      <B110>4999999</B110>
    </B100>
    <B500>
      <B540>
        <B542 lang="en">INVENTION TITLE WITHOUT KIND CODE</B542>
      </B540>
    </B500>
  </SDOBI>
</ep-patent-document>
"""

class TestPhase6BFederatedRetrieval(unittest.TestCase):

    # ------------------------------------------------------------------
    # A. KIND-CODE SAFETY & XML PARSER INTEGRITY
    # ------------------------------------------------------------------
    def test_epo_xml_parser_full_document(self):
        """Verifies parsing of complete ep-patent-document with all fields."""
        doc = EPOXMLParser.parse_ep_document(SAMPLE_EPO_XML)
        self.assertEqual(doc["publication_number"], "EP4812013")
        self.assertEqual(doc["country"], "EP")
        self.assertEqual(doc["kind_code"], "A1")  # Verified kind code preserved
        self.assertEqual(doc["publication_date"], "2026-09-30")
        self.assertEqual(doc["title"], "METHOD FOR PRODUCTION OF PRECISION RETINAL MAPS")
        self.assertIn("deep learning based retinal image analysis", doc["abstract"])
        self.assertEqual(len(doc["applicants"]), 2)
        self.assertEqual(doc["applicants"][0], "KITE TECHNOLOGIES GMBH")
        self.assertEqual(len(doc["inventors"]), 2)
        self.assertIn("DR. SZABO, Levente", doc["inventors"])
        self.assertEqual(len(doc["ipc"]), 2)
        self.assertEqual(len(doc["cpc"]), 1)
        self.assertIsNotNone(doc["claims"])
        self.assertIsNotNone(doc["description"])
        self.assertEqual(doc["source"], "EPO_EPS")

    def test_epo_xml_parser_missing_fields_never_fabricates_kind_code(self):
        """Proves that missing kind_code returns None and is NEVER inferred as 'A'."""
        doc = EPOXMLParser.parse_ep_document(SAMPLE_EPO_XML_MISSING_OPTIONAL)
        self.assertEqual(doc["publication_number"], "EP4999999")
        self.assertIsNone(doc["kind_code"])  # MUST be None, never "A"
        self.assertIsNone(doc["publication_date"])  # MUST be None, never "2020-01-01"
        self.assertEqual(doc["title"], "INVENTION TITLE WITHOUT KIND CODE")
        self.assertIsNone(doc["abstract"])
        self.assertEqual(doc["applicants"], [])
        self.assertEqual(doc["inventors"], [])

    def test_epo_xml_parser_malformed_xml_handling(self):
        """Verifies malformed XML raises ValueError gracefully without unhandled crashes."""
        with self.assertRaises(ValueError):
            EPOXMLParser.parse_ep_document("<ep-patent-document><unclosed></ep-patent-document>")

    # ------------------------------------------------------------------
    # B. PROVIDER ABSTRACTION & LOCAL SOURCE
    # ------------------------------------------------------------------
    def test_local_patent_source_properties_and_metadata(self):
        """Verifies LocalPatentSource adheres to PatentSource interface and metadata."""
        src = LocalPatentSource()
        self.assertEqual(src.name, "LOCAL_PATENTIQ")
        meta = src.get_metadata()
        self.assertEqual(meta["source"], "LOCAL_PATENTIQ")
        self.assertTrue(meta["offline_capable"])

    def test_local_patent_source_search_tags_provenance(self):
        """Verifies search results through LocalPatentSource are tagged with LOCAL_PATENTIQ."""
        src = LocalPatentSource()
        # Mock execute_nl_hybrid_search
        mock_result = PatentSearchResult(
            patent_id="loc_1",
            publication_number="201941048032",
            title="Local Patent Title",
            country="IN",
            source="LOCAL_PATENTIQ",
            final_score=0.88
        )
        with patch("backend.patent_sources.local_source.execute_nl_hybrid_search", return_value=[mock_result]):
            results = src.search("diabetic retinopathy", top_k=1)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].source, "LOCAL_PATENTIQ")

    # ------------------------------------------------------------------
    # C. EPO CLIENT & USAGE TRACKING (FAIR-USE BANDWIDTH PROTECTION)
    # ------------------------------------------------------------------
    def test_epo_usage_tracker_sliding_window_and_safety_cutoff(self):
        """Verifies usage tracking and safety cutoff (90% of budget = 4.5 GB)."""
        tmp_usage_file = "data/cache/test_epo_usage_tmp.json"
        tracker = EPOUsageTracker(
            usage_file=tmp_usage_file,
            limit_bytes=1000,
            safety_threshold_ratio=0.90  # 900 bytes threshold
        )
        try:
            self.assertTrue(tracker.can_request())

            # Record 500 bytes -> under 900 limit
            tracker.record_request(500, status_code=200, endpoint="publication-dates")
            self.assertEqual(tracker.get_rolling_7_day_bytes(), 500)
            self.assertTrue(tracker.can_request())

            # Record another 450 bytes -> 950 bytes total >= 900 safety limit
            tracker.record_request(450, status_code=200, endpoint="patents")
            self.assertEqual(tracker.get_rolling_7_day_bytes(), 950)
            self.assertFalse(tracker.can_request())  # Must throttle!

            summary = tracker.get_usage_summary()
            self.assertTrue(summary["is_throttled"])
            self.assertEqual(summary["requests_in_window"], 2)
        finally:
            if os.path.exists(tmp_usage_file):
                os.remove(tmp_usage_file)

    def test_epo_client_skips_when_throttled(self):
        """Proves EPO client does not make outbound HTTP requests when usage budget is exceeded."""
        client = EPOClient()
        with patch("backend.patent_sources.epo_client.USAGE_TRACKER.can_request", return_value=False):
            res = client.fetch_patent_xml("EP4812013")
            self.assertIsNone(res)

    # ------------------------------------------------------------------
    # D. EPO DOCUMENT CACHING
    # ------------------------------------------------------------------
    def test_epo_cache_hit_and_miss_lifecycle(self):
        """Verifies caching avoids duplicate fetches for identical EP identifiers."""
        test_cache_dir = "data/cache/test_epo_cache_dir"
        cache = EPOCache(cache_dir=test_cache_dir, enabled=True)
        try:
            self.assertIsNone(cache.get("EP4812013"))
            self.assertEqual(cache.misses, 1)

            dummy_data = {"publication_number": "EP4812013", "title": "Cached Retinal Map"}
            cache.set("EP4812013", dummy_data)

            hit_doc = cache.get("EP4812013")
            self.assertIsNotNone(hit_doc)
            self.assertEqual(hit_doc["title"], "Cached Retinal Map")
            self.assertEqual(cache.hits, 1)
        finally:
            if os.path.exists(test_cache_dir):
                import shutil
                shutil.rmtree(test_cache_dir)

    # ------------------------------------------------------------------
    # E. CROSS-SOURCE DEDUPLICATION & RESULT FUSION
    # ------------------------------------------------------------------
    def test_result_fusion_deduplication_and_provenance_merging(self):
        """Proves identical patent across local and EPO merges into single canonical result with fused provenance."""
        local_p1 = PatentSearchResult(
            patent_id="p1",
            publication_number="EP4812013",
            title="Local Title",
            country="EP",
            document_number="4812013",
            source="LOCAL_PATENTIQ",
            final_score=0.85,
            ranking_reasons=["Local hybrid vector match"]
        )
        local_p2 = PatentSearchResult(
            patent_id="p2",
            publication_number="201941048032",
            title="Indian Local Patent",
            country="IN",
            document_number="201941048032",
            source="LOCAL_PATENTIQ",
            final_score=0.78,
            ranking_reasons=["Local text match"]
        )
        epo_live = PatentSearchResult(
            patent_id="epo_EP4812013",
            publication_number="EP4812013",
            title="Local Title",
            country="EP",
            document_number="4812013",
            source="EPO_EPS",
            final_score=0.92,
            ranking_reasons=["Live EPO concept match"]
        )

        fused, meta = ResultFusion.fuse(
            local_results=[local_p1, local_p2],
            live_results=[epo_live],
            top_k=5
        )

        # 3 items input -> 2 items output due to deduplication of EP4812013
        self.assertEqual(len(fused), 2)
        self.assertEqual(meta["duplicates_merged"], 1)

        # First item should be EP4812013 with merged provenance
        ep_res = next(r for r in fused if r.publication_number == "EP4812013")
        self.assertEqual(ep_res.source, "LOCAL_PATENTIQ + EPO_EPS")
        self.assertEqual(ep_res.final_score, 0.92)
        self.assertIn("Live EPO concept match", ep_res.ranking_reasons)
        self.assertIn("Local hybrid vector match", ep_res.ranking_reasons)

    # ------------------------------------------------------------------
    # F. EPO FAILURE & GRACEFUL FALLBACK (CRITICAL NON-BLOCKING REQUIREMENT)
    # ------------------------------------------------------------------
    def test_epo_failure_falls_back_cleanly_to_local_results(self):
        """Proves that when EPO throws network timeout or HTTP 500, local search succeeds seamlessly."""
        from backend.api.services.orchestrator import PatentIntelligenceService

        mock_vs = MagicMock()
        mock_vs.db_path = "data/vectordb"
        service = PatentIntelligenceService(vector_store=mock_vs)

        # Simulate local results
        mock_local_result = PatentSearchResult(
            patent_id="in_1",
            publication_number="201941048032",
            title="Robust Local Patent",
            country="IN",
            document_number="201941048032",
            source="LOCAL_PATENTIQ",
            final_score=0.88
        )
        from backend.retrieval.query_model import NLSearchResponse
        from backend.llm.query_understanding import plan_patent_query

        dummy_query = plan_patent_query("Diabetic retinopathy detection")
        dummy_resp = NLSearchResponse(
            query="Diabetic retinopathy detection",
            interpreted_query=dummy_query,
            search_strategy={},
            total_results=1,
            results=[mock_local_result],
            ranking_information={},
            source_metadata={}
        )

        with patch("backend.api.services.orchestrator.execute_nl_hybrid_search", return_value=dummy_resp):
            with patch("backend.patent_sources.epo_publication_source.EPO_CLIENT.fetch_patent_xml", side_effect=TimeoutError("EPO Network Timeout")):
                response = service.search_natural_language(
                    query="Diabetic retinopathy detection",
                    top_k=5,
                    source_mode="hybrid"
                )

                # Local results MUST be returned
                self.assertEqual(len(response.results), 1)
                self.assertEqual(response.results[0].publication_number, "201941048032")
                self.assertEqual(response.results[0].source, "LOCAL_PATENTIQ")
                self.assertIsNotNone(response.provenance_metadata)
                self.assertEqual(response.provenance_metadata["local_results_count"], 1)

    # ------------------------------------------------------------------
    # G. API SOURCE MODE COMPATIBILITY
    # ------------------------------------------------------------------
    def test_api_source_modes(self):
        """Verifies source_mode='local' bypasses live EPO completely."""
        from backend.api.services.orchestrator import PatentIntelligenceService

        mock_vs = MagicMock()
        mock_vs.db_path = "data/vectordb"
        service = PatentIntelligenceService(vector_store=mock_vs)

        mock_local_result = PatentSearchResult(
            patent_id="loc_1",
            publication_number="1/CHE/2010",
            title="Local Indian Patent",
            country="IN",
            document_number="1/CHE/2010",
            source="LOCAL_PATENTIQ",
            final_score=0.90
        )
        from backend.retrieval.query_model import NLSearchResponse
        from backend.llm.query_understanding import plan_patent_query

        dummy_query = plan_patent_query("Cataract treatment")
        dummy_resp = NLSearchResponse(
            query="Cataract treatment",
            interpreted_query=dummy_query,
            search_strategy={},
            total_results=1,
            results=[mock_local_result],
            ranking_information={},
            source_metadata={}
        )

        with patch("backend.api.services.orchestrator.execute_nl_hybrid_search", return_value=dummy_resp):
            with patch("backend.patent_sources.epo_publication_source.EPOPublicationSource.search") as mock_epo_search:
                # Mode = local -> must NOT invoke EPO search at all
                resp_local = service.search_natural_language("Cataract treatment", source_mode="local")
                mock_epo_search.assert_not_called()
                self.assertEqual(resp_local.source_mode, "local")
                self.assertFalse(resp_local.provenance_metadata["live_retrieval_used"])

if __name__ == "__main__":
    unittest.main()
