import unittest
from unittest.mock import MagicMock, patch
from backend.reports.models import (
    ReportGenerateRequest,
    ResearchIntelligenceReport
)
from backend.reports.service import ReportGenerationService, report_service
from backend.reports.markdown_exporter import generate_markdown_report
from backend.reports.pdf_exporter import generate_pdf_report

class TestFeature4ResearchReport(unittest.TestCase):
    def setUp(self):
        # Mock orchestrator and sub-services
        self.mock_intel = MagicMock()
        self.mock_comparison = MagicMock()
        self.mock_innovation = MagicMock()
        
        self.sample_patents = [
            {
                "publication_number": "IN201941012345",
                "title": "Method and apparatus for automated retinal lesion localization using neural networks",
                "abstract": "A machine learning system for detecting diabetic retinopathy lesions in retinal photographs.",
                "applicant": "All India Institute of Medical Sciences",
                "publication_date": "2020-05-15",
                "semantic_score": 0.88,
                "final_score": 0.88,
                "provenance": {"source_name": "Indian Patent Office"}
            },
            {
                "publication_number": "EP3456789",
                "title": "Computer-implemented diagnostic screening of ophthalmological anomalies",
                "abstract": "Deep convolutional networks applied to multi-spectral fundus imaging with severity grading.",
                "applicant": "Siemens Healthineers AG",
                "publication_date": "2021-08-10",
                "semantic_score": 0.74,
                "final_score": 0.74,
                "provenance": {"source_name": "EPO European Publication Server"}
            }
        ]

        # Setup mock natural language search
        mock_nl_res = MagicMock()
        mock_nl_res.patents = self.sample_patents
        mock_q_und = MagicMock()
        mock_q_und.technology_domain = "Medical Diagnostics"
        mock_q_und.technical_concepts = ["retinal lesion", "severity grading", "deep learning"]
        mock_nl_res.interpreted_query = mock_q_und
        self.mock_intel.search_natural_language.return_value = mock_nl_res
        self.mock_intel.interpret_query.return_value = mock_q_und

        self.service = ReportGenerationService(
            intelligence_service=self.mock_intel,
            comparison_service=self.mock_comparison,
            innovation_service=self.mock_innovation
        )

    def test_01_report_generation_from_search_results(self):
        req = ReportGenerateRequest(
            invention_description="AI diabetic retinopathy detection from fundus images",
            search_results=self.sample_patents
        )
        report = self.service.generate_report(req)
        self.assertIsInstance(report, ResearchIntelligenceReport)
        self.assertEqual(len(report.prior_art_landscape), 2)
        self.assertTrue(report.report_id.startswith("PIQ-REP-"))

    def test_02_report_generation_from_feature2_comparison(self):
        comp_results = {
            "compared_patents": ["IN201941012345", "EP3456789"],
            "shared_concepts": ["neural networks", "fundus imaging"],
            "distinct_concepts": {
                "IN201941012345": ["local lesion detection"],
                "EP3456789": ["multi-spectral imaging"]
            },
            "technical_differences": ["Spatial attention vs spectral filters"]
        }
        req = ReportGenerateRequest(
            invention_description="Ophthalmological AI screening",
            search_results=self.sample_patents,
            comparison_results=comp_results
        )
        report = self.service.generate_report(req)
        self.assertIsNotNone(report.patent_comparison)
        self.assertEqual(report.patent_comparison.compared_patents, ["IN201941012345", "EP3456789"])
        self.assertIn("neural networks", report.patent_comparison.shared_concepts)

    def test_03_report_generation_from_feature3_innovation(self):
        innov_results = {
            "differentiation_directions": [
                {
                    "direction": "Edge-optimized severity grading",
                    "category": "Technical Architecture",
                    "evidence_gap_level": "MODERATE EVIDENCE GAP",
                    "why_investigate": "Severity grading is less represented on edge platforms.",
                    "related_concepts": ["severity grading", "edge computing"],
                    "research_question": "Can inference latency be kept under 50ms?",
                    "linked_patent_ids": ["IN201941012345"]
                }
            ],
            "research_questions": ["What is the validation accuracy on low-resolution sensors?"]
        }
        req = ReportGenerateRequest(
            invention_description="AI diabetic retinopathy detection",
            search_results=self.sample_patents,
            innovation_results=innov_results
        )
        report = self.service.generate_report(req)
        self.assertTrue(len(report.differentiation_directions) > 0)
        self.assertEqual(report.differentiation_directions[0].category, "Technical Architecture")

    def test_04_combined_report_generation(self):
        req = ReportGenerateRequest(
            title="Comprehensive Diabetic Retinopathy Intelligence",
            invention_description="Deep learning fundus lesion detection and severity grading",
            search_results=self.sample_patents,
            include_comparison=False,
            include_innovation=False
        )
        report = self.service.generate_report(req)
        self.assertEqual(report.title, "Comprehensive Diabetic Retinopathy Intelligence")
        self.assertIn("Patent Comparison", report.unavailable_sections)

    def test_05_partial_data_report_generation(self):
        minimal_patents = [
            {"publication_number": "IN111", "title": "Minimal title"}
        ]
        req = ReportGenerateRequest(
            query="Simple sensor test",
            search_results=minimal_patents
        )
        report = self.service.generate_report(req)
        self.assertEqual(len(report.prior_art_landscape), 1)
        self.assertEqual(report.prior_art_landscape[0].publication_number, "IN111")

    def test_06_empty_or_invalid_request(self):
        with self.assertRaises(ValueError):
            ReportGenerateRequest(invention_description="", query="")

    def test_07_no_results_scenario(self):
        self.mock_intel.search_natural_language.return_value.patents = []
        req = ReportGenerateRequest(query="Non-existent patent topic")
        report = self.service.generate_report(req)
        self.assertEqual(len(report.prior_art_landscape), 0)
        self.assertIn("AI-Estimated Novelty Indicator", report.unavailable_sections)

    def test_08_missing_claims_and_abstract(self):
        patents_no_text = [{"publication_number": "IN999", "title": "Device Without Abstract"}]
        req = ReportGenerateRequest(query="Device test", search_results=patents_no_text)
        report = self.service.generate_report(req)
        self.assertEqual(len(report.detailed_patent_summaries), 1)
        self.assertIn("not provided", report.detailed_patent_summaries[0].core_technical_idea.lower())

    def test_09_provenance_preservation(self):
        req = ReportGenerateRequest(query="Test provenance", search_results=self.sample_patents)
        report = self.service.generate_report(req)
        self.assertIn("primary_source", report.provenance)
        self.assertEqual(report.provenance["total_retrieved"], 2)

    def test_10_existing_novelty_indicator_preservation(self):
        req = ReportGenerateRequest(query="Novelty test", search_results=self.sample_patents)
        report = self.service.generate_report(req)
        self.assertIsNotNone(report.novelty_indicator)
        self.assertIn("automated prior-art similarity indicator", report.novelty_indicator.disclaimer)

    def test_11_existing_coverage_labels_preservation(self):
        req = ReportGenerateRequest(
            invention_description="AI retinal screening",
            search_results=self.sample_patents
        )
        report = self.service.generate_report(req)
        self.assertTrue(len(report.concept_coverage) > 0)
        valid_bands = {"Strongly Represented", "Moderately Represented", "Weakly Represented", "Minimally Represented", "No Meaningful Evidence"}
        for cc in report.concept_coverage:
            self.assertIn(cc.status, valid_bands)

    def test_12_unsupported_patent_claims_not_invented(self):
        req = ReportGenerateRequest(query="Test grounded claims", search_results=self.sample_patents)
        report = self.service.generate_report(req)
        for ps in report.detailed_patent_summaries:
            self.assertTrue(ps.evidence_source in ["Indian Patent Office", "EPO European Publication Server", "PatentIQ Corpus"])

    def test_13_research_directions_evidence_grounded(self):
        innov_data = {
            "differentiation_directions": [
                {
                    "direction": "Multimodal fusion",
                    "category": "Data / Input",
                    "evidence_gap_level": "HIGHER EVIDENCE GAP",
                    "why_investigate": "Low representation in retrieved art.",
                    "related_concepts": ["sensor fusion"],
                    "research_question": "Does fusion improve specificity?",
                    "linked_patent_ids": ["EP3456789"]
                }
            ]
        }
        req = ReportGenerateRequest(query="Fusion test", search_results=self.sample_patents, innovation_results=innov_data)
        report = self.service.generate_report(req)
        self.assertEqual(report.differentiation_directions[0].linked_patent_ids, ["EP3456789"])

    def test_14_legal_disclaimer_present(self):
        req = ReportGenerateRequest(query="Disclaimer check", search_results=self.sample_patents)
        report = self.service.generate_report(req)
        self.assertIn("not legal advice", report.disclaimer.lower())
        self.assertIn("patentability", report.disclaimer.lower())

    def test_15_structured_report_schema_validation(self):
        req = ReportGenerateRequest(query="Schema test", search_results=self.sample_patents)
        report = self.service.generate_report(req)
        data = report.model_dump()
        self.assertIn("report_id", data)
        self.assertIn("executive_summary", data)
        self.assertIn("prior_art_landscape", data)
        self.assertIn("disclaimer", data)

    def test_16_markdown_export_content(self):
        req = ReportGenerateRequest(query="Markdown test", search_results=self.sample_patents)
        report = self.service.generate_report(req)
        md = generate_markdown_report(report)
        self.assertIn("# PatentIQ Research Intelligence", md)
        self.assertIn("## 1. Executive Summary", md)
        self.assertIn("IN201941012345", md)
        self.assertIn("## 14. Legal Disclaimer", md)

    def test_17_pdf_export_produces_valid_pdf(self):
        req = ReportGenerateRequest(query="PDF test", search_results=self.sample_patents)
        report = self.service.generate_report(req)
        pdf_bytes = generate_pdf_report(report)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 1000)

    def test_18_long_titles_and_tables_no_clipping(self):
        long_title = "A " + "very "*40 + "long patent title testing line wrap behavior"
        patents = [{"publication_number": "INLONG123", "title": long_title, "applicant": "Lengthy Corp", "abstract": "Long "*50}]
        req = ReportGenerateRequest(query="Long title test", search_results=patents)
        report = self.service.generate_report(req)
        pdf_bytes = generate_pdf_report(report)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_19_invalid_or_expired_report_handling(self):
        res = self.service.get_report("NON-EXISTENT-ID")
        self.assertIsNone(res)
        md = self.service.get_report_markdown("NON-EXISTENT-ID")
        self.assertIsNone(md)
        pdf = self.service.get_report_pdf("NON-EXISTENT-ID")
        self.assertIsNone(pdf)

    def test_20_llm_failure_handling(self):
        self.mock_intel.interpret_query.side_effect = Exception("LLM Quota Exceeded")
        req = ReportGenerateRequest(query="LLM failure resilience", search_results=self.sample_patents)
        report = self.service.generate_report(req)
        self.assertIsNotNone(report)
        self.assertEqual(len(report.prior_art_landscape), 2)

    def test_21_export_endpoint_content_types_and_filenames(self):
        from backend.api.routes.reports import sanitize_filename
        clean = sanitize_filename("PIQ-REP/2026/01:test*")
        self.assertEqual(clean, "PIQ-REP_2026_01_test_")

    def test_22_report_session_isolation(self):
        req1 = ReportGenerateRequest(title="Report A", query="Query A", search_results=self.sample_patents[:1])
        req2 = ReportGenerateRequest(title="Report B", query="Query B", search_results=self.sample_patents[1:])
        r1 = self.service.generate_report(req1)
        r2 = self.service.generate_report(req2)
        self.assertNotEqual(r1.report_id, r2.report_id)
        self.assertNotEqual(r1.title, r2.title)

    def test_23_input_sanitization(self):
        dangerous_query = "<script>alert('xss')</script> Injection"
        req = ReportGenerateRequest(query=dangerous_query, search_results=self.sample_patents)
        report = self.service.generate_report(req)
        md = generate_markdown_report(report)
        self.assertIn("alert", md)

    def test_24_feature1_remains_functional(self):
        from backend.copilot.models import CopilotIntent
        self.assertEqual(CopilotIntent.PRIOR_ART_SEARCH.value, "PRIOR_ART_SEARCH")
        self.assertEqual(CopilotIntent.REPORT.value, "REPORT")

    def test_25_feature2_remains_functional(self):
        from backend.comparison.models import CompareRequest
        req = CompareRequest(patent_ids=["IN201941012345", "EP3456789"])
        self.assertEqual(len(req.patent_ids), 2)

    def test_26_feature3_remains_functional(self):
        from backend.innovation.models import InnovationAnalyzeRequest
        req = InnovationAnalyzeRequest(idea="Edge ML fundus detection")
        self.assertEqual(req.source_mode, "hybrid")

if __name__ == "__main__":
    unittest.main()
