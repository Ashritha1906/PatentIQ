import os

import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest

from backend.intelligence.novelty_scoring import calculate_novelty_score, NOVELTY_DISCLAIMER

from backend.intelligence.innovation_gap import (

    score_concept_coverage, 

    detect_innovation_gaps, 

    COVERAGE_THRESHOLDS,

    get_coverage_band

)

from backend.retrieval.identifier_normalizer import (

    normalize_patent_identifier,

    normalize_patent_record

)



class TestPhase6A1Corrections(unittest.TestCase):

    

    # ----------------------------------------------------

    # 1. NOVELTY SCORE CONSISTENCY & CANONICAL VALUE TESTS

    # ----------------------------------------------------

    def test_novelty_canonical_score_consistency(self):

        """Proves all novelty outputs (score, novelty_score, overall_novelty_score) match identically."""

        sample_patents = [

            {"similarity_score": 0.85, "title": "Test Patent 1", "patent_text": "AI vision", "field_of_invention": "ELECTRICAL"},

            {"similarity_score": 0.65, "title": "Test Patent 2", "patent_text": "Sensors", "field_of_invention": "ELECTRICAL"}

        ]

        query_understanding = {

            "keywords": ["ai", "vision", "autonomous"],

            "technology_domain": "ELECTRICAL"

        }

        res = calculate_novelty_score(sample_patents, query_understanding)

        

        # Verify all three keys exist and are exactly identical

        self.assertIn("score", res)

        self.assertIn("novelty_score", res)

        self.assertIn("overall_novelty_score", res)

        self.assertEqual(res["score"], res["novelty_score"])

        self.assertEqual(res["score"], res["overall_novelty_score"])

        

        # Verify explanation text contains the exact score

        expected_substr = f"{res['score']}/100"

        self.assertIn(expected_substr, res["explanation"])



    def test_novelty_terminology_and_disclaimer(self):

        """Verifies AI-estimated terminology and mandatory disclaimer."""

        res = calculate_novelty_score([], {})

        self.assertEqual(res["indicator_name"], "AI-Estimated Novelty Indicator")

        self.assertEqual(res["disclaimer"], NOVELTY_DISCLAIMER)

        self.assertIn(NOVELTY_DISCLAIMER, res["explanation"])

        self.assertNotIn("guaranteed patentability", res["explanation"].lower())

        self.assertNotIn("legal novelty", res["explanation"].lower())



    # ----------------------------------------------------

    # 2. CONCEPT COVERAGE & SEMANTIC EQUIVALENCE TESTS

    # ----------------------------------------------------

    def test_semantic_equivalence_not_marked_missing(self):

        """Proves 'Retinal fundus images' is NOT marked 'Missing' when 'fundus imaging' is present."""

        patents = [

            {

                "application_number": "201941048032",

                "title": "SYSTEM FOR FUNDUS IMAGING AND RETINAL ANALYSIS",

                "patent_text": "Apparatus for capturing fundus images for diabetic retinopathy diagnosis.",

                "field_of_invention": "BIO-MEDICAL ENGINEERING"

            }

        ]

        eval_res = score_concept_coverage("Retinal fundus images", patents)

        

        # Must be recognized semantically

        self.assertFalse(eval_res["exact_phrase_present"])

        self.assertTrue(eval_res["semantic_concept_present"])

        self.assertGreaterEqual(eval_res["coverage_score"], 50.0)

        self.assertNotEqual(eval_res["coverage_band"], "No Meaningful Evidence")

        self.assertIn(eval_res["coverage_band"], ("Moderately Represented", "Strongly Represented"))

        self.assertTrue(len(eval_res["matched_equivalents"]) > 0)



    def test_exact_phrase_marked_exact(self):

        """Proves exact phrase match is correctly flagged as exact."""

        patents = [

            {

                "application_number": "201811024989",

                "title": "DEEP LEARNING MODEL FOR IMAGE CLASSIFICATION",

                "patent_text": "Discloses a deep learning neural network.",

                "field_of_invention": "COMPUTER SCIENCE"

            }

        ]

        eval_res = score_concept_coverage("deep learning", patents)

        self.assertTrue(eval_res["exact_phrase_present"])

        self.assertTrue(eval_res["semantic_concept_present"])

        self.assertGreaterEqual(eval_res["coverage_score"], 60.0)



    def test_true_missing_concept_scored_zero(self):

        """Proves absent technical concept receives 0 score and 'No Meaningful Evidence'."""

        patents = [

            {

                "application_number": "1/CHE/2010",

                "title": "WIND TURBINE BLADE PITCH CONTROLLER",

                "patent_text": "Aerodynamic rotor blade control system.",

                "field_of_invention": "MECHANICAL"

            }

        ]

        eval_res = score_concept_coverage("quantum key distribution", patents)

        self.assertEqual(eval_res["coverage_score"], 0.0)

        self.assertEqual(eval_res["coverage_band"], "No Meaningful Evidence")

        self.assertFalse(eval_res["exact_phrase_present"])

        self.assertFalse(eval_res["semantic_concept_present"])



    # ----------------------------------------------------

    # 3. WHITESPACE CLASSIFICATION & COMBINATION GAPS

    # ----------------------------------------------------

    def test_whitespace_distinguishes_exact_from_semantic(self):

        """Verifies whitespace detection does not label semantic matches as 'Missing'."""

        patents = [

            {

                "application_number": "201941048032",

                "title": "A RETINAL IMAGING METHOD",

                "patent_text": "Fundus image capture with neural network.",

                "field_of_invention": "BIO-MEDICAL ENGINEERING"

            }

        ]

        qu = {

            "technical_concepts": ["retinal fundus images", "severity grading"]

        }

        gaps = detect_innovation_gaps(patents, qu)

        

        # 'retinal fundus images' has semantic presence -> must NOT be in opportunities as 'Missing'

        missing_concepts = [g["concept"] for g in gaps if g["representation_status"] == "Missing" and not g.get("is_combination")]

        self.assertNotIn("retinal fundus images", missing_concepts)

        

        # 'severity grading' is truly missing -> must be in gaps

        self.assertIn("severity grading", missing_concepts)



    def test_combination_level_whitespace_detected(self):

        """Verifies combination whitespace when individual concepts exist separately but not together."""

        patents = [

            {

                "application_number": "1/CHE/2010",

                "title": "Deep learning system",

                "patent_text": "Neural network model.",

                "field_of_invention": "AI"

            },

            {

                "application_number": "2/CHE/2010",

                "title": "Fundus camera hardware",

                "patent_text": "Optical fundus camera.",

                "field_of_invention": "MEDICAL"

            }

        ]

        qu = {

            "technical_concepts": ["deep learning", "fundus camera", "real-time tele-ophthalmology", "severity grading"]

        }

        gaps = detect_innovation_gaps(patents, qu)

        combo_gaps = [g for g in gaps if g.get("is_combination", False)]

        self.assertTrue(len(combo_gaps) >= 1)

        self.assertTrue("Combination" in combo_gaps[0]["concept"] or "System" in combo_gaps[0]["concept"])



    # ----------------------------------------------------

    # 4. PATENT IDENTIFIER NORMALIZATION AUDIT TESTS

    # ----------------------------------------------------

    def test_normalize_regional_office_slash_format(self):

        """Verifies regional office slash format (e.g. 1/CHE/2010, 9990/DELNP/2011)."""

        id1 = normalize_patent_identifier("1/CHE/2010")

        self.assertEqual(id1["publication_number"], "1/CHE/2010")

        self.assertEqual(id1["country"], "IN")

        self.assertIsNone(id1["kind_code"])

        self.assertEqual(id1["publication_year"], 2010)



        id2 = normalize_patent_identifier("9990/DELNP/2011")

        self.assertEqual(id2["publication_number"], "9990/DELNP/2011")

        self.assertEqual(id2["country"], "IN")

        self.assertEqual(id2["publication_year"], 2011)



    def test_normalize_modern_12_digit_format(self):

        """Verifies modern 12-digit IPO format (e.g. 201941048032)."""

        id1 = normalize_patent_identifier("201941048032")

        self.assertEqual(id1["publication_number"], "201941048032")

        self.assertEqual(id1["country"], "IN")

        self.assertIsNone(id1["kind_code"])

        self.assertEqual(id1["publication_year"], 2019)



    def test_normalize_patent_record_enrichment(self):

        """Verifies dictionary enrichment preserves metadata while adding canonical fields."""

        rec = {

            "application_number": "201811024989",

            "title": "SAMPLE INVENTIVE TITLE",

            "publication_date": "2018-05-12"

        }

        norm = normalize_patent_record(rec)

        self.assertEqual(norm["publication_number"], "201811024989")

        self.assertEqual(norm["country"], "IN")

        self.assertIsNone(norm["kind_code"])

        self.assertEqual(norm["document_number"], "201811024989")

        self.assertEqual(norm["publication_date"], "2018-05-12")

    def test_normalize_preserves_verified_kind_code_and_handles_missing(self):
        """Proves verified kind codes are preserved while missing kind codes return None."""
        # International with verified kind code
        us_doc = normalize_patent_identifier("US10123456B2")
        self.assertEqual(us_doc["kind_code"], "B2")
        self.assertEqual(us_doc["country"], "US")

        ep_doc = normalize_patent_identifier("EP3124567A1")
        self.assertEqual(ep_doc["kind_code"], "A1")
        self.assertEqual(ep_doc["country"], "EP")

        # International without explicit kind code -> must return None, never infer "A"
        wo_doc = normalize_patent_identifier("WO2021012345")
        self.assertIsNone(wo_doc["kind_code"])

        # Record with verified kind_code provided in source
        rec_verified = {"publication_number": "201941048032", "kind_code": "B"}
        self.assertEqual(normalize_patent_record(rec_verified)["kind_code"], "B")

        # Record without kind_code in source -> must return None
        rec_no_kind = {"publication_number": "201941048032"}
        self.assertIsNone(normalize_patent_record(rec_no_kind)["kind_code"])

    def test_normalize_preserves_publication_date_only_when_supported(self):
        """Proves publication_date is preserved when present and never fabricated when missing."""
        rec_with_date = {"publication_number": "1/CHE/2010", "publication_date": "2011-07-08"}
        norm_with_date = normalize_patent_record(rec_with_date)
        self.assertEqual(norm_with_date["publication_date"], "2011-07-08")

        rec_no_date = {"publication_number": "1/CHE/2010"}
        norm_no_date = normalize_patent_record(rec_no_date)
        self.assertIsNone(norm_no_date["publication_date"])




    # ----------------------------------------------------

    # 5. RESILIENCE: MISSING METADATA & ZERO RESULTS

    # ----------------------------------------------------

    def test_novelty_and_gaps_zero_results_resilience(self):

        """Verifies zero results produce clean fallback without crashing."""

        nov = calculate_novelty_score([], {})

        self.assertEqual(nov["score"], 100)

        self.assertEqual(nov["band"], "Highly Differentiated")



        gaps = detect_innovation_gaps([], {})

        self.assertTrue(len(gaps) >= 1)

        self.assertEqual(gaps[0]["coverage_score"], 0.0)



    def test_coverage_missing_fields_resilience(self):

        """Verifies evaluation handles patents with None or missing abstract/text."""

        sparse_pat = [{"application_number": "1/MUM/2012", "title": None, "patent_text": None}]

        eval_res = score_concept_coverage("solar inverter", sparse_pat)

        self.assertEqual(eval_res["coverage_score"], 0.0)



if __name__ == "__main__":

    unittest.main()

