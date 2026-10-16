import unittest
from unittest.mock import patch, MagicMock
from backend.comparison.models import (
    CompareRequest,
    DeepDiveRequest,
    PatentComparisonResponse,
    DeepDiveResponse,
)
from backend.comparison.engine import PatentComparisonEngine
from backend.copilot.models import CopilotTurn, CopilotIntent
from backend.copilot.context import CopilotSession
from backend.copilot.service import CopilotService

class TestFeature2PatentComparison(unittest.TestCase):
    def setUp(self):
        self.engine = PatentComparisonEngine()
        self.p1 = {
            "publication_number": "IN202011001",
            "title": "Automated drone surveillance using convolutional neural networks",
            "abstract": "A system using camera streams and CNN for detecting objects.",
            "applicant": "DroneTech Ltd",
            "publication_date": "2021-04-12",
            "classification": "G06V",
            "claims": "1. An aerial monitoring apparatus comprising an optical camera and a CNN processor.",
            "provenance": {"source": "LOCAL", "identifier": "IN202011001", "confidence": "HIGH"}
        }
        self.p2 = {
            "publication_number": "EP3456789",
            "title": "Ground sensor telemetry with temporal risk forecasting",
            "abstract": "Distributed environmental sensors with temporal sequence prediction.",
            "applicant": "EcoSensors SE",
            "publication_date": "2020-09-18",
            "classification": "G08B",
            "provenance": {"source": "EPO_EPS", "identifier": "EP3456789", "confidence": "HIGH"}
        }
        self.p3 = {
            "publication_number": "US9988776",
            "title": "Satellite multispectral thermal imaging for environmental risk assessment",
            "abstract": "Thermal band imaging sensor analysis for early hazard alerting.",
            "applicant": "OrbitAnalytics Inc",
            "publication_date": "2022-01-05",
            "classification": "G01N",
            "provenance": {"source": "LOCAL", "identifier": "US9988776", "confidence": "HIGH"}
        }

    # 1. Two-patent selection
    @patch("backend.comparison.engine.generate_text", return_value="Mocked AI comparison summary.")
    def test_01_two_patent_selection(self, mock_llm):
        req = CompareRequest(patents=[self.p1, self.p2])
        res = self.engine.compare(req)
        self.assertEqual(len(res.patents), 2)
        self.assertIn("IN202011001", [p.get("publication_number") for p in res.patents])
        self.assertIn("EP3456789", [p.get("publication_number") for p in res.patents])
        self.assertEqual(len(res.technical_similarities), 1)

    # 2. Three-patent selection
    @patch("backend.comparison.engine.generate_text", return_value="Mocked 3-patent AI summary.")
    def test_02_three_patent_selection(self, mock_llm):
        req = CompareRequest(patents=[self.p1, self.p2, self.p3])
        res = self.engine.compare(req)
        self.assertEqual(len(res.patents), 3)
        self.assertEqual(len(res.technical_similarities), 3)  # AB, AC, BC

    # 3. More-than-three rejection
    def test_03_more_than_three_rejection(self):
        p4 = dict(self.p1, publication_number="IN4444")
        with self.assertRaises(ValueError) as ctx:
            CompareRequest(patents=[self.p1, self.p2, self.p3, p4])
        self.assertIn("limited to 3", str(ctx.exception).lower())

    # 4. Fewer-than-two rejection
    def test_04_fewer_than_two_rejection(self):
        with self.assertRaises(ValueError) as ctx:
            CompareRequest(patents=[self.p1])
        self.assertIn("at least 2", str(ctx.exception).lower())

    # 5. Invalid patent ID handling
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_05_invalid_patent_id_handling(self, mock_llm):
        req = CompareRequest(patent_ids=["NONEXISTENT_999", "INVALID_000"])
        res = self.engine.compare(req)
        self.assertEqual(len(res.patents), 2)
        # Should create partial data placeholder without crashing
        self.assertTrue(res.patents[0].get("partial_data"))
        self.assertEqual(res.patents[0].get("publication_number"), "NONEXISTENT_999")
        self.assertEqual(res.patents[1].get("publication_number"), "INVALID_000")

    # 6. Comparison API schema validation
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_06_comparison_api_schema(self, mock_llm):
        req = CompareRequest(patents=[self.p1, self.p2])
        res = self.engine.compare(req)
        self.assertIsInstance(res, PatentComparisonResponse)
        d = res.model_dump()
        for field in ["patents", "summary", "matrix", "shared_concepts", "distinct_concepts", "key_differences", "combination_gaps", "technical_similarities", "disclaimer"]:
            self.assertIn(field, d)
        self.assertIn("NOT constitute a legal determination", d["disclaimer"])

    # 7. Core invention extraction
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_07_core_invention_extraction(self, mock_llm):
        req = CompareRequest(patents=[self.p1, self.p2])
        res = self.engine.compare(req)
        dim = next(d for d in res.matrix if d.dimension == "Core Invention")
        self.assertIn("IN202011001", dim.values)
        self.assertIn("EP3456789", dim.values)
        self.assertIn("CNN", dim.values["IN202011001"])

    # 8. Technical approach comparison
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_08_technical_approach_comparison(self, mock_llm):
        req = CompareRequest(patents=[self.p1, self.p2])
        res = self.engine.compare(req)
        dim = next(d for d in res.matrix if d.dimension == "Technical Approach")
        self.assertIsNotNone(dim.values.get("IN202011001"))
        self.assertIsNotNone(dim.values.get("EP3456789"))

    # 9. Shared concept extraction
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_09_shared_concept_extraction(self, mock_llm):
        p_shared1 = dict(self.p1, abstract="Sensor data transmission over satellite network")
        p_shared2 = dict(self.p2, abstract="Distributed sensor processing with satellite uplink")
        req = CompareRequest(patents=[p_shared1, p_shared2])
        res = self.engine.compare(req)
        shared_lower = [c.lower() for c in res.shared_concepts]
        self.assertTrue(any("sensor" in c or "satellite" in c for c in shared_lower))

    # 10. Distinct concept extraction
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_10_distinct_concept_extraction(self, mock_llm):
        req = CompareRequest(patents=[self.p1, self.p2])
        res = self.engine.compare(req)
        self.assertIn("IN202011001", res.distinct_concepts)
        self.assertIn("EP3456789", res.distinct_concepts)
        p1_distinct = [c.lower() for c in res.distinct_concepts["IN202011001"]]
        self.assertTrue(any("drone" in c or "neural" in c or "cnn" in c for c in p1_distinct))

    # 11. Combination-gap reuse
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_11_combination_gap_reuse(self, mock_llm):
        req = CompareRequest(patents=[self.p1, self.p2])
        res = self.engine.compare(req)
        self.assertTrue(len(res.combination_gaps) >= 1)
        gap = res.combination_gaps[0]
        self.assertIn("less represented", gap["description"].lower())
        self.assertNotIn("novel", gap["description"].lower())
        self.assertNotIn("patentable", gap["description"].lower())

    # 12. Missing evidence handling
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_12_missing_evidence_handling(self, mock_llm):
        p_sparse = {
            "publication_number": "SPARSE_001",
            "title": "Minimal title",
            "abstract": None,
            "applicant": None
        }
        req = CompareRequest(patents=[self.p1, p_sparse])
        res = self.engine.compare(req)
        dim_applicant = next(d for d in res.matrix if d.dimension == "Applicant")
        self.assertEqual(dim_applicant.values["SPARSE_001"], "Not available in retrieved evidence.")

    # 13. No hallucinated technical method
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_13_no_hallucinated_technical_method(self, mock_llm):
        # p2 has no ML mentioned
        req = CompareRequest(patents=[self.p1, self.p2])
        res = self.engine.compare(req)
        dim_ml = next(d for d in res.matrix if d.dimension == "AI / ML Methods")
        self.assertIn("Cnn", dim_ml.values["IN202011001"])
        self.assertEqual(dim_ml.values["EP3456789"], "Not available in retrieved evidence.")

    # 14. Claim information handling
    def test_14_claim_information_handling(self):
        # With claims
        req_with_claims = DeepDiveRequest(patent=self.p1)
        res1 = self.engine.deep_dive(req_with_claims)
        self.assertIn("The retrieved claim text focuses on:", res1.claim_focus)
        self.assertIn("aerial monitoring apparatus", res1.claim_focus)

        # Without claims
        req_no_claims = DeepDiveRequest(patent=self.p2)
        res2 = self.engine.deep_dive(req_no_claims)
        self.assertEqual(res2.claim_focus, "Claim information is not available in the retrieved source.")

    # 15. Provenance preservation
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_15_provenance_preservation(self, mock_llm):
        req = CompareRequest(patents=[self.p1, self.p2])
        res = self.engine.compare(req)
        self.assertEqual(res.patents[0]["provenance"]["source"], "LOCAL")
        self.assertEqual(res.patents[1]["provenance"]["source"], "EPO_EPS")

    # 16. Partial retrieval handling
    @patch("backend.comparison.engine.generate_text", return_value="Mock summary.")
    def test_16_partial_retrieval_handling(self, mock_llm):
        p_partial = {
            "publication_number": "PARTIAL_777",
            "title": "Partial document",
            "abstract": "Not available in retrieved evidence.",
            "partial_data": True
        }
        req = CompareRequest(patents=[self.p1, p_partial])
        res = self.engine.compare(req)
        self.assertEqual(len(res.patents), 2)
        self.assertTrue(res.patents[1]["partial_data"])

    # 17. LLM failure handling
    @patch("backend.comparison.engine.generate_text", side_effect=Exception("API Quota Exceeded"))
    def test_17_llm_failure_handling(self, mock_llm):
        req = CompareRequest(patents=[self.p1, self.p2])
        res = self.engine.compare(req)
        self.assertIsInstance(res.summary, str)
        self.assertTrue(len(res.summary) > 20)
        self.assertIn("IN202011001", res.summary)

    # 18. Feature 1 Copilot integration
    @patch("backend.comparison.engine.generate_text", return_value="Grounded technical comparison via copilot.")
    def test_18_copilot_integration(self, mock_llm):
        copilot = CopilotService()
        session = CopilotSession(session_id="test_compare_sess")
        session.retrieved_patents = [self.p1, self.p2]
        resp = copilot._handle_compare("Compare top two patents", session, {})
        self.assertEqual(resp.intent, CopilotIntent.COMPARE.value)
        self.assertIn("IN202011001", resp.message)
        self.assertIn("Deep dive into", resp.suggested_followups[0])
        self.assertEqual(len(resp.patents), 2)

    # 19. Existing PatentCard compatibility
    def test_19_patent_card_compatibility(self):
        # Ensures that compared patent objects have all attributes expected by PatentCard
        req = CompareRequest(patents=[self.p1, self.p2])
        for p in req.patents:
            self.assertIn("publication_number", p)
            self.assertIn("title", p)
            self.assertIn("applicant", p)

    # 20. Deep Dive response schema and distinction in set
    def test_20_deep_dive_schema_and_distinction(self):
        req = DeepDiveRequest(patent=self.p1, comparison_context=[self.p1, self.p2])
        res = self.engine.deep_dive(req)
        self.assertIsInstance(res, DeepDiveResponse)
        self.assertEqual(res.patent_id, "IN202011001")
        self.assertIsNotNone(res.distinction_in_set)
        self.assertIn("Distinct within the selected comparison set", res.distinction_in_set)
        self.assertTrue(len(res.research_questions) >= 3)
        self.assertIn("NOT constitute legal claim construction", res.disclaimer)

if __name__ == "__main__":
    unittest.main()