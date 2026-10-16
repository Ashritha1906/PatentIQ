import unittest
from unittest.mock import patch, MagicMock
from backend.innovation.models import (
    InnovationAnalyzeRequest,
    InnovationAnalysisResponse,
    DifferentiationDirection,
    ConceptCoverageItem,
)
from backend.innovation.service import InnovationRefinementService
from backend.copilot.context import CopilotSession
from backend.copilot.service import CopilotService

class TestFeature3InnovationRefinement(unittest.TestCase):
    def setUp(self):
        self.mock_intel = MagicMock()
        self.p1 = {
            "application_number": "IN202011001",
            "publication_number": "IN202011001",
            "title": "Automated retinal fundus image processing with convolutional neural network",
            "abstract": "A deep learning CNN system for automated diabetic retinopathy detection from fundus images.",
            "applicant": "OphthalmoAI Corp",
            "publication_date": "2021-04-12",
            "field_of_invention": "MEDICAL AI",
            "similarity_score": 0.82,
            "provenance": {"source": "LOCAL", "identifier": "IN202011001", "confidence": "HIGH"}
        }
        self.p2 = {
            "application_number": "EP3456789",
            "publication_number": "EP3456789",
            "title": "Clinical telemetry screening for ophthalmic conditions",
            "abstract": "Patient medical telemetry aggregated with optical sensor imaging.",
            "applicant": "HealthTech Europe",
            "publication_date": "2020-09-18",
            "field_of_invention": "MEDICAL DIAGNOSTICS",
            "similarity_score": 0.55,
            "provenance": {"source": "EPO_EPS", "identifier": "EP3456789", "confidence": "HIGH"}
        }
        self.mock_context = {
            "retrieved_patents": [self.p1, self.p2],
            "query_understanding": {
                "technology_domain": "MEDICAL AI",
                "keywords": ["diabetic retinopathy", "fundus images", "deep learning", "lesion detection", "severity grading"],
                "core_concepts": ["automated detection", "retinal images"]
            }
        }
        self.mock_intel._retrieve_context.return_value = self.mock_context
        self.service = InnovationRefinementService(intelligence_service=self.mock_intel)

    # 1. Valid innovation analysis
    def test_01_valid_innovation_analysis(self):
        req = InnovationAnalyzeRequest(
            idea="I am building an AI system that detects diabetic retinopathy from retinal fundus images using deep learning with lesion-level severity grading."
        )
        res = self.service.analyze_innovation(req)
        self.assertIsInstance(res, InnovationAnalysisResponse)
        self.assertEqual(len(res.retrieved_patents), 2)
        self.assertFalse(res.insufficient_evidence)
        self.assertTrue(len(res.differentiation_directions) >= 2)

    # 2. Empty idea rejection
    def test_02_empty_idea_rejection(self):
        with self.assertRaises(ValueError) as ctx:
            InnovationAnalyzeRequest(idea="   ")
        self.assertIn("cannot be empty", str(ctx.exception).lower())

    # 3. Short / insufficient idea handling
    def test_03_short_insufficient_idea(self):
        req = InnovationAnalyzeRequest(idea="AI for images")
        res = self.service.analyze_innovation(req)
        self.assertTrue(res.insufficient_evidence)
        self.assertEqual(len(res.retrieved_patents), 0)
        self.assertTrue(len(res.research_questions) >= 2)

    # 4. Retrieval integration
    def test_04_retrieval_integration(self):
        req = InnovationAnalyzeRequest(idea="Automated diabetic retinopathy detection using retinal fundus images.")
        res = self.service.analyze_innovation(req)
        self.mock_intel._retrieve_context.assert_called_once()
        self.assertIn("IN202011001", [p.get("publication_number") for p in res.retrieved_patents])

    # 5. Concept coverage reuse
    def test_05_concept_coverage_reuse(self):
        req = InnovationAnalyzeRequest(idea="Automated diabetic retinopathy detection using retinal fundus images and severity grading.")
        res = self.service.analyze_innovation(req)
        self.assertIn("strongly_represented", res.concept_coverage)
        self.assertIn("weakly_represented", res.concept_coverage)
        total_concepts = sum(len(items) for items in res.concept_coverage.values())
        self.assertTrue(total_concepts >= 3)

    # 6. Whitespace reuse
    def test_06_whitespace_reuse(self):
        req = InnovationAnalyzeRequest(idea="Automated diabetic retinopathy detection using retinal fundus images and lesion detection.")
        res = self.service.analyze_innovation(req)
        self.assertIsInstance(res.combination_gaps, list)

    # 7. Combination-gap reuse
    def test_07_combination_gap_reuse(self):
        req = InnovationAnalyzeRequest(idea="Automated diabetic retinopathy detection with severity grading and edge inference.")
        res = self.service.analyze_innovation(req)
        # Any combination gaps surfaced must have safe terminology
        for gap in res.combination_gaps:
            self.assertIn("less represented", gap["description"].lower())
            self.assertNotIn("novel", gap["description"].lower())
            self.assertNotIn("patentable", gap["description"].lower())

    # 8. Novelty indicator reuse
    def test_08_novelty_indicator_reuse(self):
        req = InnovationAnalyzeRequest(idea="Automated diabetic retinopathy detection from fundus images.")
        res = self.service.analyze_innovation(req)
        self.assertIn("score", res.novelty_indicator)
        self.assertIn("band", res.novelty_indicator)
        self.assertIn("AI-Estimated Novelty Indicator", res.novelty_indicator["indicator_name"])
        self.assertIn("disclaimer", res.novelty_indicator)

    # 9. Differentiation generation
    def test_09_differentiation_generation(self):
        req = InnovationAnalyzeRequest(idea="AI diabetic retinopathy detection from fundus images.")
        res = self.service.analyze_innovation(req)
        self.assertTrue(len(res.differentiation_directions) >= 2)
        d1 = res.differentiation_directions[0]
        self.assertIsInstance(d1, DifferentiationDirection)
        self.assertIn(d1.category, ["Technical Architecture", "Data / Input", "Processing Pipeline", "AI / ML Methods", "System Combination"])
        self.assertTrue(len(d1.research_questions) >= 1)

    # 10. Evidence grounding
    def test_10_evidence_grounding(self):
        req = InnovationAnalyzeRequest(idea="AI diabetic retinopathy detection with lesion localization.")
        res = self.service.analyze_innovation(req)
        for direction in res.differentiation_directions:
            self.assertTrue(len(direction.related_patent_ids) >= 1)
            self.assertTrue(len(direction.related_concepts) >= 1)

    # 11. No unsupported novelty claim
    def test_11_no_unsupported_novelty_claim(self):
        req = InnovationAnalyzeRequest(idea="AI diabetic retinopathy detection from fundus images.")
        res = self.service.analyze_innovation(req)
        full_text = str(res.model_dump()).lower()
        self.assertNotIn("your idea is definitely novel", full_text)
        self.assertNotIn("guarantees novelty", full_text)

    # 12. No patentability claim
    def test_12_no_patentability_claim(self):
        req = InnovationAnalyzeRequest(idea="AI diabetic retinopathy detection from fundus images.")
        res = self.service.analyze_innovation(req)
        full_text = str(res.model_dump()).lower()
        self.assertNotIn("patentable invention", full_text)
        self.assertNotIn("guaranteed patentability", full_text)
        self.assertIn("not a legal determination of patentability", res.disclaimer.lower())

    # 13. No global uniqueness claim
    def test_13_no_global_uniqueness_claim(self):
        req = InnovationAnalyzeRequest(idea="AI diabetic retinopathy detection from fundus images.")
        res = self.service.analyze_innovation(req)
        full_text = str(res.model_dump()).lower()
        self.assertNotIn("no patent covers this", full_text)
        self.assertNotIn("nobody has patented this", full_text)

    # 14. Insufficient evidence handling
    def test_14_insufficient_evidence_handling(self):
        empty_intel = MagicMock()
        empty_intel._retrieve_context.return_value = {
            "retrieved_patents": [],
            "query_understanding": {"technology_domain": "GENERAL", "keywords": []}
        }
        empty_service = InnovationRefinementService(intelligence_service=empty_intel)
        req = InnovationAnalyzeRequest(idea="Quantum antigravity warp drive reactor.")
        res = empty_service.analyze_innovation(req)
        self.assertTrue(res.insufficient_evidence)
        self.assertEqual(len(res.retrieved_patents), 0)
        self.assertIn("not have enough relevant prior-art evidence", res.novelty_indicator["explanation"].lower())

    # 15. Provenance preservation
    def test_15_provenance_preservation(self):
        req = InnovationAnalyzeRequest(idea="AI diabetic retinopathy detection from fundus images.")
        res = self.service.analyze_innovation(req)
        self.assertIsNotNone(res.provenance)
        self.assertIn(res.provenance.get("source"), ["LOCAL", "EPO_EPS", "HYBRID"])

    # 16. Feature 1 Copilot integration
    def test_16_copilot_integration(self):
        copilot = CopilotService()
        session = CopilotSession(session_id="test_innov_sess")
        session.retrieved_patents = [self.p1, self.p2]
        session.current_query = "AI diabetic retinopathy detection"
        resp = copilot._handle_improve_idea("How can I differentiate my idea?", session)
        self.assertIn("Research Differentiation Directions", resp.message)
        self.assertIn("AI-Estimated Novelty Indicator", resp.message)

    # 17. Feature 2 context integration
    def test_17_feature2_context_integration(self):
        p3 = {
            "application_number": "US9988776",
            "publication_number": "US9988776",
            "title": "Satellite multispectral thermal imaging",
            "abstract": "Thermal sensor analysis.",
            "field_of_invention": "AEROSPACE",
            "similarity_score": 0.40,
            "provenance": {"source": "LOCAL", "identifier": "US9988776", "confidence": "HIGH"}
        }
        req = InnovationAnalyzeRequest(
            idea="AI diabetic retinopathy detection from fundus images.",
            comparison_context=[p3]
        )
        res = self.service.analyze_innovation(req)
        ids = [p.get("publication_number") for p in res.retrieved_patents]
        self.assertIn("US9988776", ids)
        self.assertEqual(len(res.retrieved_patents), 3)

    # 18. API schema validation
    def test_18_api_schema_validation(self):
        req = InnovationAnalyzeRequest(idea="AI diabetic retinopathy detection from fundus images.")
        res = self.service.analyze_innovation(req)
        d = res.model_dump()
        for k in ["idea_summary", "technology_domain", "retrieved_patents", "novelty_indicator", "concept_coverage", "idea_vs_prior_art", "combination_gaps", "differentiation_directions", "research_questions", "disclaimer"]:
            self.assertIn(k, d)

    # 19. Retrieval failure fallback
    def test_19_retrieval_failure_fallback(self):
        fail_intel = MagicMock()
        fail_intel._retrieve_context.side_effect = RuntimeError("Vector store timeout")
        fail_service = InnovationRefinementService(intelligence_service=fail_intel)
        req = InnovationAnalyzeRequest(idea="AI diabetic retinopathy detection from fundus images.")
        res = fail_service.analyze_innovation(req)
        self.assertTrue(res.insufficient_evidence)

    # 20. LLM failure handling
    @patch("backend.innovation.service.generate_text", side_effect=Exception("LLM Quota Exceeded"))
    def test_20_llm_failure_handling(self, mock_llm):
        req = InnovationAnalyzeRequest(idea="AI diabetic retinopathy detection from fundus images with severity grading.")
        res = self.service.analyze_innovation(req)
        self.assertIsInstance(res, InnovationAnalysisResponse)
        self.assertTrue(len(res.differentiation_directions) >= 2)

if __name__ == "__main__":
    unittest.main()
