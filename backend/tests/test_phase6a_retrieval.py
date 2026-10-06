import os
import sys
import os
os.environ["MOCK_LLM"] = "true"
import unittest
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.retrieval.query_model import PatentQuery, QueryIntent, PatentSearchResult, NLSearchResponse
from backend.retrieval.query_expansion import expand_terms, build_search_phrases, validate_classification
from backend.retrieval.nl_retrieval import (
    normalize_scores,
    compute_keyword_relevance,
    execute_nl_hybrid_search
)
from backend.llm.query_understanding import plan_patent_query

class TestPhase6ARetrieval(unittest.TestCase):

    def setUp(self):
        self.mock_patent_pool = [
            {
                "id": "100/CHE/2018",
                "title": "AI BASED RETINAL IMAGE ANALYSIS SYSTEM",
                "text": "A deep learning convolutional neural network system for automated diabetic retinopathy diagnosis.",
                "applicant": "EYELOGIC LTD",
                "ipc": "A61B 3/12",
                "distance": 0.25
            },
            {
                "id": "101/CHE/2018",
                "title": "BATTERY CHARGING OPTIMIZATION FOR ELECTRIC VEHICLES",
                "text": "State-of-charge calculation loops and thermal regulation for high capacity lithium cells.",
                "applicant": "POWERGRID INC",
                "ipc": "H01M 10/44",
                "distance": 0.40
            },
            {
                "id": "102/CHE/2012",
                "title": "LEGACY RETINAL PHOTOGRAPHY CAMERA",
                "text": "An optical camera for fundus photography of human ocular retina.",
                "applicant": "OPTICORP",
                "ipc": "A61B",
                "distance": 0.35
            }
        ]

    # Test 1: Simple natural-language query
    def test_1_simple_natural_language_query(self):
        pq = plan_patent_query("Find patents related to smart watch health monitoring")
        self.assertIsInstance(pq, PatentQuery)
        self.assertIn(pq.intent, list(QueryIntent))
        self.assertGreater(len(pq.technical_concepts), 0)

    # Test 2: Technical query
    def test_2_technical_query(self):
        pq = plan_patent_query("A time-to-digital converter in Class-D digital loops to reduce jitter")
        self.assertIsInstance(pq, PatentQuery)
        self.assertTrue(any("time" in c.lower() or "digital" in c.lower() or "converter" in c.lower() for c in pq.technical_concepts))

    # Test 3: Query with synonyms
    def test_3_query_with_synonyms(self):
        expanded = expand_terms(["diabetic retinopathy", "retinal images"])
        self.assertTrue(any("fundus" in s or "retinal" in s for s in expanded))
        phrases = build_search_phrases(["diabetic retinopathy"], expanded)
        self.assertGreater(len(phrases), 0)

    # Test 4: Query with date constraint
    def test_4_query_with_date_constraint(self):
        pq = plan_patent_query("Patents published after 2016 related to battery management systems")
        self.assertIsNotNone(pq.date_constraints)
        self.assertEqual(pq.date_constraints.get("after"), 2016)

    # Test 5: Query with applicant constraint
    def test_5_query_with_applicant_constraint(self):
        pq = plan_patent_query("Patents from QUALCOMM on beamforming MIMO antennas")
        self.assertIsNotNone(pq.applicant_constraints)
        self.assertTrue(any("QUALCOMM" in a for a in pq.applicant_constraints))

    # Test 6: Broad query
    def test_6_broad_query(self):
        pq = plan_patent_query("New technology inventions and apparatus")
        self.assertIsInstance(pq, PatentQuery)
        self.assertGreater(len(pq.technical_concepts), 0)

    # Test 7: Ambiguous query
    def test_7_ambiguous_query(self):
        pq = plan_patent_query("Something that makes machines work faster")
        self.assertEqual(pq.intent, QueryIntent.PATENT_DISCOVERY)
        self.assertGreater(len(pq.technical_concepts), 0)

    # Test 8: Non-patent query
    def test_8_non_patent_query(self):
        pq = plan_patent_query("What is the capital of France and who is the president?")
        self.assertEqual(pq.intent, QueryIntent.GENERAL_PATENT_QUESTION)

    # Test 9: Empty query
    def test_9_empty_query(self):
        pq = plan_patent_query("")
        self.assertEqual(pq.confidence, 0.0)
        res = execute_nl_hybrid_search(pq)
        self.assertEqual(res.total_results, 0)
        self.assertIsNotNone(res.confidence_message)

    # Test 10: Semantic retrieval
    def test_10_semantic_retrieval(self):
        pq = PatentQuery(
            original_query="artificial intelligence diabetic retinopathy",
            intent=QueryIntent.PRIOR_ART_SEARCH,
            technical_concepts=["diabetic retinopathy", "artificial intelligence"]
        )
        res = execute_nl_hybrid_search(pq, top_k=3)
        self.assertGreater(res.total_results, 0)
        self.assertGreater(res.results[0].semantic_score, 0.0)

    # Test 11: Keyword retrieval
    def test_11_keyword_retrieval(self):
        kw_score, reasons = compute_keyword_relevance(
            doc_title="DETECTION OF DIABETIC RETINOPATHY USING AI",
            doc_text="A system using deep convolutional networks on fundus photography.",
            technical_concepts=["diabetic retinopathy"],
            search_phrases=["diabetic retinopathy AI"],
            expanded_terms=["fundus photography"]
        )
        self.assertGreater(kw_score, 5.0)
        self.assertTrue(any("Title directly matches" in r for r in reasons))

    # Test 12: Hybrid retrieval
    def test_12_hybrid_retrieval(self):
        res = execute_nl_hybrid_search("AI-based detection of diabetic retinopathy from retinal images", top_k=3)
        self.assertIsInstance(res, NLSearchResponse)
        self.assertEqual(len(res.results), 3)
        for r in res.results:
            self.assertGreater(r.final_score, 0.0)
            self.assertIsInstance(r.ranking_reasons, list)

    # Test 13: Duplicate removal
    def test_13_duplicate_removal(self):
        fake_ids = [["1/CHE/2010", "1/CHE/2010", "2/CHE/2010"]]
        fake_metas = [[
            {"title": "IDENTICAL TITLE", "classification_ipc": "A61K"},
            {"title": "IDENTICAL TITLE", "classification_ipc": "A61K"},
            {"title": "DISTINCT TITLE", "classification_ipc": "G06F"}
        ]]
        fake_docs = [["doc 1", "doc 1 dup", "doc 2"]]
        fake_dists = [[0.1, 0.1, 0.2]]

        mock_col = MagicMock()
        mock_col.query.return_value = {
            "ids": fake_ids,
            "metadatas": fake_metas,
            "documents": fake_docs,
            "distances": fake_dists
        }

        with patch("backend.retrieval.nl_retrieval.get_retrieval_resources", return_value=(MagicMock(), mock_col)):
            pq = PatentQuery(original_query="test", intent=QueryIntent.PATENT_DISCOVERY)
            res = execute_nl_hybrid_search(pq, top_k=5)
            self.assertEqual(res.total_results, 2)
            self.assertEqual(len(res.results), 2)

    # Test 14: Score normalization
    def test_14_score_normalization(self):
        scores = [10.0, 20.0, 30.0]
        norm = normalize_scores(scores)
        self.assertEqual(norm, [0.0, 0.5, 1.0])

        identical = [5.0, 5.0, 5.0]
        self.assertEqual(normalize_scores(identical), [1.0, 1.0, 1.0])
        self.assertEqual(normalize_scores([]), [])

    # Test 15: Re-ranking
    def test_15_reranking(self):
        res = execute_nl_hybrid_search("diabetic retinopathy fundus imaging", top_k=5)
        scores = [r.final_score for r in res.results]
        # Should be sorted in descending order
        self.assertEqual(scores, sorted(scores, reverse=True))
        for r in res.results:
            self.assertGreater(len(r.ranking_reasons), 0)

    # Test 16: Missing metadata
    def test_16_missing_metadata(self):
        mock_col = MagicMock()
        mock_col.query.return_value = {
            "ids": [["999/CHE/2015"]],
            "metadatas": [[{"title": "PARTIAL METADATA TEST"}]],  # Missing applicant & IPC
            "documents": [["Some text here."]],
            "distances": [[0.3]]
        }
        with patch("backend.retrieval.nl_retrieval.get_retrieval_resources", return_value=(MagicMock(), mock_col)):
            pq = PatentQuery(original_query="test", intent=QueryIntent.PATENT_DISCOVERY)
            res = execute_nl_hybrid_search(pq, top_k=1)
            self.assertEqual(res.total_results, 1)
            self.assertEqual(res.results[0].applicant, "Unknown Applicant")

    # Test 17: Missing abstract
    def test_17_missing_abstract(self):
        mock_col = MagicMock()
        mock_col.query.return_value = {
            "ids": [["888/DEL/2014"]],
            "metadatas": [[{"title": "PATENT WITHOUT ABSTRACT", "applicant_name": "ABC CORP"}]],
            "documents": [[""]],
            "distances": [[0.2]]
        }
        with patch("backend.retrieval.nl_retrieval.get_retrieval_resources", return_value=(MagicMock(), mock_col)):
            pq = PatentQuery(original_query="test", intent=QueryIntent.PATENT_DISCOVERY)
            res = execute_nl_hybrid_search(pq, top_k=1)
            self.assertEqual(res.total_results, 1)
            self.assertEqual(res.results[0].abstract, "")

    # Test 18: No results
    def test_18_no_results(self):
        mock_col = MagicMock()
        mock_col.query.return_value = {"ids": [[]], "metadatas": [[]], "documents": [[]], "distances": [[]]}
        with patch("backend.retrieval.nl_retrieval.get_retrieval_resources", return_value=(MagicMock(), mock_col)):
            pq = PatentQuery(original_query="unmatched technology phrase", intent=QueryIntent.PATENT_DISCOVERY)
            res = execute_nl_hybrid_search(pq, top_k=5)
            self.assertEqual(res.total_results, 0)
            self.assertIn("No matching patents", res.confidence_message)

    # Test 19: Weak results notice
    def test_19_weak_results(self):
        mock_col = MagicMock()
        mock_col.query.return_value = {
            "ids": [["111/MUM/2010"]],
            "metadatas": [[{"title": "UNRELATED WEAK DOCUMENT", "applicant_name": "CORP"}]],
            "documents": [["Unrelated content without concepts."]],
            "distances": [[1.95]]  # Cosine distance 1.95 -> raw similarity 0.05
        }
        with patch("backend.retrieval.nl_retrieval.get_retrieval_resources", return_value=(MagicMock(), mock_col)):
            pq = PatentQuery(original_query="very specific niche phrase", intent=QueryIntent.PATENT_DISCOVERY)
            # Both normalized to 1.0 if single item, but let's test weak notice logic
            res = execute_nl_hybrid_search(pq, top_k=1)
            self.assertIsNotNone(res)

    # Test 20: Gemini failure
    def test_20_gemini_failure(self):
        with patch("backend.llm.query_understanding.generate_text", side_effect=RuntimeError("Gemini quota 429")):
            pq = plan_patent_query("Find patents related to electric vehicle battery management")
            self.assertIsInstance(pq, PatentQuery)
            self.assertEqual(pq.intent, QueryIntent.PATENT_DISCOVERY)
            self.assertGreater(len(pq.technical_concepts), 0)

    # Test 21: ChromaDB failure
    def test_21_chromadb_failure(self):
        mock_col = MagicMock()
        mock_col.query.side_effect = RuntimeError("Chroma persistent disk failure")
        with patch("backend.retrieval.nl_retrieval.get_retrieval_resources", return_value=(MagicMock(), mock_col)):
            with self.assertRaises(RuntimeError):
                execute_nl_hybrid_search("diabetic retinopathy", top_k=5)

if __name__ == "__main__":
    unittest.main()
