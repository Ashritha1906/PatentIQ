import unittest
from backend.knowledge_expansion.parser import parse_lens_patent, map_ipc_to_domain
from backend.knowledge_expansion.normalizer import normalize_patent, normalize_applicant

class TestParserAndNormalizer(unittest.TestCase):
    """Unit tests for patent parsing, technology mapping, and data normalizations."""

    def setUp(self):
        # Sample Lens JSON response object structure
        self.raw_lens_patent = {
            "lens_id": "001-223-456",
            "doc_key": "US_11023456_B1",
            "biblio": {
                "title": [{"text": "High Performance Consensual Node Networking", "lang": "en"}],
                "application": {"number": "US202111023456A"},
                "publication_number": "US11023456B1",
                "publication_date": "2023-05-15",
                "applicants": [
                    {"extracted_name": {"value": "QUALCOMM INCORPORATED"}},
                    {"extracted_name": {"value": "QUALCOMM TECHNOLOGIES CO"}}
                ],
                "classifications_ipc": {
                    "classifications": [
                        {"symbol": "H04W72/04"},
                        {"symbol": "G06F16/23"}
                    ]
                }
            },
            "abstract": [{"text": "An apparatus and system for handling consensus...", "lang": "en"}]
        }

    def test_parse_lens_patent_success(self):
        """Verifies successful mapping of Lens record to internal schema."""
        parsed = parse_lens_patent(self.raw_lens_patent)
        
        self.assertEqual(parsed["application_number"], "US202111023456A")
        self.assertEqual(parsed["title"], "High Performance Consensual Node Networking")
        self.assertEqual(parsed["publication_number"], "US11023456B1")
        self.assertEqual(parsed["publication_date"], "2023-05-15")
        self.assertIn("QUALCOMM INCORPORATED", parsed["applicant_name"])
        self.assertIn("H04W72/04", parsed["classification_ipc"])
        # Priority mapping should hit H04W -> COMMUNICATION
        self.assertEqual(parsed["field_of_invention"], "COMMUNICATION")

    def test_map_ipc_to_domain_rules(self):
        """Verifies domain classifications resolver based on IPC prefixes."""
        self.assertEqual(map_ipc_to_domain(["G06F17/30"]), "COMPUTER SCIENCE")
        self.assertEqual(map_ipc_to_domain(["H04L29/06"]), "COMMUNICATION")
        self.assertEqual(map_ipc_to_domain(["A61B5/00"]), "BIO-MEDICAL ENGINEERING")
        self.assertEqual(map_ipc_to_domain(["C12N15/11"]), "BIOTECHNOLOGY")
        self.assertEqual(map_ipc_to_domain(["H01M10/05"]), "ELECTRICAL")
        self.assertEqual(map_ipc_to_domain(["F03D1/06"]), "MECHANICAL ENGINEERING")
        self.assertEqual(map_ipc_to_domain(["H01L21/02"]), "ELECTRONICS")
        self.assertEqual(map_ipc_to_domain([]), "COMPUTER SCIENCE") # fallback

    def test_normalize_applicant_dedup_and_suffix_removal(self):
        """Verifies organization suffix stripping and duplicate removals."""
        raw_name = "QUALCOMM INCORPORATED; QUALCOMM TECHNOLOGIES CO; QUALCOMM INC"
        norm = normalize_applicant(raw_name)
        # Suffixes stripped and deduplicated down to single entity name
        self.assertEqual(norm, "QUALCOMM")

    def test_normalize_patent_builds_text_representation(self):
        """Verifies full normalization completes and structures the embedding text template."""
        parsed = parse_lens_patent(self.raw_lens_patent)
        normalized = normalize_patent(parsed)
        
        # Verify text layout format template
        expected_text = (
            "Title: High Performance Consensual Node Networking\n\n"
            "Field Of Invention: COMMUNICATION\n\n"
            "IPC Classification: H04W72/04, G06F16/23\n\n"
            "Applicant: QUALCOMM"
        )
        self.assertEqual(normalized["patent_text"], expected_text)

if __name__ == "__main__":
    unittest.main()
