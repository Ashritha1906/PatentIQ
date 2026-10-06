import unittest
from unittest.mock import MagicMock, patch
from backend.copilot.models import (
    CopilotIntent,
    CopilotChatRequest,
    CopilotChatResponse,
    ResearchContextSummary
)
from backend.copilot.context import CopilotSession, SessionManager, session_manager
from backend.copilot.intent import classify_intent
from backend.copilot.resolver import (
    resolve_target_patent,
    resolve_comparison_targets,
    extract_specific_technical_inquiry
)
from backend.copilot.service import CopilotService
from backend.retrieval.query_model import PatentSearchResult, NLSearchResponse, PatentQuery

class TestFeature1Copilot(unittest.TestCase):
    def setUp(self):
        self.service = CopilotService()
        self.gen_patcher = patch("backend.copilot.service.generate_text", return_value="AI synthesis grounded in retrieved prior art text.")
        self.mock_generate_text = self.gen_patcher.start()

        self.sample_patents = [
            {
                "publication_number": "IN201941048032",
                "application_number": "201941048032",
                "title": "Autonomous Wildfire Detection Using Satellite Imagery and CNN",
                "applicant": "ISRO",
                "classification": "G06T7/00",
                "abstract": "An autonomous forest fire and wildfire detection system utilizing multi-spectral satellite imagery and deep convolutional neural networks to localize thermal anomalies.",
                "semantic_score": 0.88,
                "source": "LOCAL_PATENTIQ"
            },
            {
                "publication_number": "EP3456789A1",
                "application_number": "EP3456789",
                "title": "Thermal Sensing and Remote Wildfire Monitoring System",
                "applicant": "European Space Agency",
                "classification": "G08B17/12",
                "abstract": "A space-borne thermal infrared sensor array configured for real-time wildfire monitoring with ground station telemetry.",
                "semantic_score": 0.74,
                "source": "EPO_EPS"
            },
            {
                "publication_number": "IN1/CHE/2010",
                "application_number": "1/CHE/2010",
                "title": "Forest Fire Alarm and Sensor Mesh",
                "applicant": "Indian Institute of Science",
                "classification": "A62C3/02",
                "abstract": "Ground sensor nodes deployed in forest canopy to detect smoke and gas emissions.",
                "semantic_score": 0.52,
                "source": "LOCAL_PATENTIQ"
            }
        ]

    def tearDown(self):
        self.gen_patcher.stop()

    # 1. Intent Classification Tests
    def test_01_intent_classification(self):
        intent, _ = classify_intent("Find patents related to AI forest fire detection")
        self.assertEqual(intent, CopilotIntent.PRIOR_ART_SEARCH)

        intent, _ = classify_intent("Explain this patent in simple words")
        self.assertEqual(intent, CopilotIntent.EXPLAIN)

        intent, _ = classify_intent("Compare the top two patents")
        self.assertEqual(intent, CopilotIntent.COMPARE)

        intent, _ = classify_intent("Summarize the patents you found")
        self.assertEqual(intent, CopilotIntent.SUMMARIZE)

        intent, _ = classify_intent("What areas are not well covered?")
        self.assertEqual(intent, CopilotIntent.WHITESPACE)

        intent, _ = classify_intent("How can I make my idea more differentiated?")
        self.assertEqual(intent, CopilotIntent.IMPROVE_IDEA)

        intent, _ = classify_intent("Generate a research report")
        self.assertEqual(intent, CopilotIntent.REPORT)

    # 2. Natural Language Query Understanding
    def test_02_query_understanding_extraction(self):
        session = CopilotSession("sess-test")
        session.retrieved_patents = self.sample_patents
        intent, details = classify_intent("Compare the first and second patent", session)
        self.assertEqual(intent, CopilotIntent.COMPARE)
        self.assertIn(0, details["referenced_indices"])
        self.assertIn(1, details["referenced_indices"])

    # 3. Prior-Art Search Execution
    def test_03_prior_art_search_flow(self):
        query_obj = PatentQuery(original_query="AI forest fire detection", technical_concepts=["wildfire", "satellite"])
        mock_response = NLSearchResponse(
            query="AI forest fire detection",
            interpreted_query=query_obj,
            search_strategy={"method": "hybrid"},
            total_results=1,
            results=[
                PatentSearchResult(
                    patent_id="IN201941048032",
                    publication_number="IN201941048032",
                    title="Autonomous Wildfire Detection",
                    abstract="Abstract here",
                    semantic_score=0.88,
                    applicant="ISRO",
                    source="LOCAL_PATENTIQ"
                )
            ],
            ranking_information={"dense_weight": 0.5, "bm25_weight": 0.5},
            source_metadata={"corpus": "Indian Patents"},
            provenance_metadata={"source_mode": "hybrid", "live_retrieval_used": True}
        )
        with patch.object(self.service.orchestrator, "search_natural_language", return_value=mock_response):
            req = CopilotChatRequest(message="Search patents for AI forest fire detection", source_mode="hybrid")
            res = self.service.handle_chat(req)
            self.assertEqual(res.intent, CopilotIntent.PRIOR_ART_SEARCH.value)
            self.assertEqual(len(res.patents), 1)
            self.assertIn("IN201941048032", res.message)
            self.assertTrue(len(res.suggested_followups) > 0)

    # 4. Explain Operation
    def test_04_explain_operation(self):
        session = session_manager.get_or_create("sess-explain")
        session.set_retrieved_patents(self.sample_patents, "wildfire detection", ["satellite", "thermal"])
        req = CopilotChatRequest(message="Explain the closest patent in simple words", session_id="sess-explain")
        res = self.service.handle_chat(req)
        self.assertEqual(res.intent, CopilotIntent.EXPLAIN.value)
        self.assertIsNotNone(res.selected_patent)
        self.assertEqual(res.selected_patent["publication_number"], "IN201941048032")

    # 5. Compare Operation
    def test_05_compare_operation(self):
        session = session_manager.get_or_create("sess-compare")
        session.set_retrieved_patents(self.sample_patents, "wildfire detection", ["satellite", "thermal"])
        req = CopilotChatRequest(message="Compare the top two patents", session_id="sess-compare")
        res = self.service.handle_chat(req)
        self.assertEqual(res.intent, CopilotIntent.COMPARE.value)
        self.assertEqual(len(res.patents), 2)

    # 6. Summarize Operation
    def test_06_summarize_operation(self):
        session = session_manager.get_or_create("sess-sum")
        session.set_retrieved_patents(self.sample_patents, "wildfire detection", ["satellite", "thermal"])
        req = CopilotChatRequest(message="Summarize the retrieved patents", session_id="sess-sum")
        res = self.service.handle_chat(req)
        self.assertEqual(res.intent, CopilotIntent.SUMMARIZE.value)
        self.assertIn("Prior Art Landscape Summary", res.message)

    # 7. Whitespace Operation (Reuses existing Phase 6A.1 engine)
    def test_07_whitespace_operation(self):
        session = session_manager.get_or_create("sess-white")
        session.set_retrieved_patents(self.sample_patents, "wildfire detection", ["satellite", "thermal", "quantum sensors"])
        req = CopilotChatRequest(message="What technology areas are not well covered?", session_id="sess-white")
        res = self.service.handle_chat(req)
        self.assertEqual(res.intent, CopilotIntent.WHITESPACE.value)
        self.assertIn("Concept Coverage Analysis", res.message)
        self.assertIn("Combination Gaps", res.message)

    # 8. Improve Idea / Differentiation Operation
    def test_08_improve_idea_differentiation(self):
        session = session_manager.get_or_create("sess-diff")
        session.set_retrieved_patents(self.sample_patents, "wildfire detection", ["satellite", "thermal"])
        req = CopilotChatRequest(message="How can I make my idea more differentiated?", session_id="sess-diff")
        res = self.service.handle_chat(req)
        self.assertEqual(res.intent, CopilotIntent.IMPROVE_IDEA.value)
        self.assertIn("AI-Estimated Novelty Indicator", res.message)
        self.assertNotIn("your invention is patentable", res.message.lower())
        self.assertNotIn("patentability guarantee", res.message.lower())

    # 9. Follow-Up Context & "Which is closest?"
    def test_09_followup_which_is_closest(self):
        session = session_manager.get_or_create("sess-closest")
        session.set_retrieved_patents(self.sample_patents, "wildfire detection", ["satellite", "thermal"])
        req = CopilotChatRequest(message="Which one is closest to my idea?", session_id="sess-closest")
        res = self.service.handle_chat(req)
        self.assertEqual(res.intent, CopilotIntent.FOLLOW_UP.value)
        self.assertIn("IN201941048032", res.message)
        self.assertEqual(session.selected_patent["publication_number"], "IN201941048032")

    # 10. Follow-Up Context & "Why?"
    def test_10_followup_why_explanation(self):
        session = session_manager.get_or_create("sess-why")
        session.set_retrieved_patents(self.sample_patents, "wildfire detection", ["satellite", "thermal"])
        session.selected_patent = self.sample_patents[0]
        req = CopilotChatRequest(message="Why?", session_id="sess-why")
        res = self.service.handle_chat(req)
        self.assertEqual(res.intent, CopilotIntent.FOLLOW_UP.value)
        self.assertIn("closest match", res.message)
        self.assertIn("IN201941048032", res.message)

    # 11. Reference Resolution for Specific Ordinal
    def test_11_reference_resolution_ordinal(self):
        session = session_manager.get_or_create("sess-ord")
        session.set_retrieved_patents(self.sample_patents, "wildfire detection", ["satellite"])
        req = CopilotChatRequest(message="Explain the second patent", session_id="sess-ord")
        res = self.service.handle_chat(req)
        self.assertEqual(res.intent, CopilotIntent.EXPLAIN.value)
        self.assertEqual(res.selected_patent["publication_number"], "EP3456789A1")

    # 12. Empty Query Resilience
    def test_12_empty_query_resilience(self):
        req = CopilotChatRequest(message="   ")
        res = self.service.handle_chat(req)
        self.assertEqual(res.intent, "IDLE")
        self.assertIn("Please provide a patent research question", res.message)

    # 13. No Results Found Handling
    def test_13_no_results_found(self):
        query_obj = PatentQuery(original_query="obscure concept")
        mock_response = NLSearchResponse(
            query="obscure concept",
            interpreted_query=query_obj,
            search_strategy={"method": "hybrid"},
            total_results=0,
            results=[],
            ranking_information={},
            source_metadata={},
            provenance_metadata={"source_mode": "hybrid"}
        )
        with patch.object(self.service.orchestrator, "search_natural_language", return_value=mock_response):
            req = CopilotChatRequest(message="Find patents for xyz non-existent", source_mode="hybrid")
            res = self.service.handle_chat(req)
            self.assertEqual(res.intent, CopilotIntent.PRIOR_ART_SEARCH.value)
            self.assertIn("No highly relevant patents were found", res.message)

    # 14. Retrieval Failure Graceful Fallback
    def test_14_retrieval_failure_fallback(self):
        with patch.object(self.service.orchestrator, "search_natural_language", side_effect=RuntimeError("VectorDB timeout")):
            req = CopilotChatRequest(message="Find patents for AI satellite", source_mode="hybrid")
            res = self.service.handle_chat(req)
            self.assertIn("error retrieving prior art", res.message.lower())

    # 15. Grounded Anti-Hallucination Behavior (Substantiated Feature)
    def test_15_grounded_substantiated_tech(self):
        session = session_manager.get_or_create("sess-tech-sub")
        session.set_retrieved_patents(self.sample_patents, "wildfire", ["satellite"])
        session.selected_patent = self.sample_patents[0] # Mentions CNN in abstract
        req = CopilotChatRequest(message="Does it use CNN?", session_id="sess-tech-sub")
        res = self.service.handle_chat(req)
        self.assertIn("explicit evidence", res.message.lower())
        self.assertIn("CNN", res.message)

    # 16. Grounded Anti-Hallucination Behavior (Unsubstantiated Feature)
    def test_16_grounded_unsubstantiated_tech_never_guesses(self):
        session = session_manager.get_or_create("sess-tech-unsub")
        session.set_retrieved_patents(self.sample_patents, "wildfire", ["satellite"])
        session.selected_patent = self.sample_patents[0]
        # Patent does NOT mention quantum cryptography
        req = CopilotChatRequest(message="Does it use quantum cryptography?", session_id="sess-tech-unsub")
        res = self.service.handle_chat(req)
        self.assertIn("does not provide enough evidence", res.message.lower())
        self.assertIn("quantum cryptography", res.message)

    # 17. Novelty Terminology and Disclaimer Enforcement
    def test_17_novelty_terminology_and_disclaimer(self):
        session = session_manager.get_or_create("sess-terms")
        session.set_retrieved_patents(self.sample_patents, "wildfire", ["satellite"])
        req = CopilotChatRequest(message="How can I differentiate my idea?", session_id="sess-terms")
        res = self.service.handle_chat(req)
        self.assertIn("AI-Estimated Novelty Indicator", res.message)
        self.assertIn("automated prior-art similarity indicator", res.disclaimer)
        self.assertNotIn("legal novelty score", res.message.lower())

    # 18. Provenance Preservation
    def test_18_provenance_preservation(self):
        session = session_manager.get_or_create("sess-prov")
        session.set_retrieved_patents(
            self.sample_patents,
            "wildfire",
            ["satellite"],
            provenance={"source_mode": "hybrid", "live_results_count": 1}
        )
        req = CopilotChatRequest(message="Explain the closest patent", session_id="sess-prov")
        res = self.service.handle_chat(req)
        self.assertIsNotNone(res.provenance)
        self.assertEqual(res.provenance["source_mode"], "hybrid")

    # 19. Session Isolation
    def test_19_session_isolation(self):
        s1 = session_manager.get_or_create("sess-user-1")
        s2 = session_manager.get_or_create("sess-user-2")
        s1.set_retrieved_patents([self.sample_patents[0]], "Topic 1", ["Concept 1"])
        s2.set_retrieved_patents([self.sample_patents[1]], "Topic 2", ["Concept 2"])
        self.assertEqual(s1.current_query, "Topic 1")
        self.assertEqual(s2.current_query, "Topic 2")
        self.assertEqual(s1.retrieved_patents[0]["publication_number"], "IN201941048032")
        self.assertEqual(s2.retrieved_patents[0]["publication_number"], "EP3456789A1")

    # 20. API Schema Validation
    def test_20_api_schema_validation(self):
        req = CopilotChatRequest(message="Test query", session_id="sess-val", source_mode="local", top_k=3)
        self.assertEqual(req.message, "Test query")
        self.assertEqual(req.source_mode, "local")
        self.assertEqual(req.top_k, 3)

        res = CopilotChatResponse(
            session_id="sess-val",
            message="Response text",
            intent="PRIOR_ART_SEARCH",
            research_context=ResearchContextSummary(intent="PRIOR_ART_SEARCH")
        )
        d = res.model_dump()
        self.assertEqual(d["session_id"], "sess-val")
        self.assertIn("disclaimer", d)

if __name__ == "__main__":
    unittest.main()
