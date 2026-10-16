import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.reports.models import (
    ReportGenerateRequest,
    ResearchIntelligenceReport,
    CoverPageInfo,
    ExecutiveSummary,
    ResearchObjective,
    MethodologyScope,
    PriorArtItem,
    DetailedPatentSummary,
    ComparisonSummary,
    NoveltyIndicatorSection,
    ReportConceptCoverageItem,
    ReportCombinationGapItem,
    ReportDifferentiationDirectionItem,
    ApplicantTrendItem,
    LimitationsSection
)
from backend.reports.markdown_exporter import generate_markdown_report
from backend.reports.pdf_exporter import generate_pdf_report

logger = logging.getLogger(__name__)

MANDATORY_DISCLAIMER = (
    "This report is generated for research and informational purposes using the PatentIQ data and analysis available "
    "at the time of generation. It is not legal advice and does not constitute a legal determination of patentability, "
    "novelty, infringement, patent validity, or freedom to operate. Findings reflect the retrieved prior-art set and "
    "may not represent all relevant patent documents worldwide. Consult a qualified patent professional for legal assessment."
)

class ReportGenerationService:
    """Consolidates PatentIQ research intelligence into a structured, evidence-grounded report."""

    def __init__(self, intelligence_service=None, comparison_service=None, innovation_service=None):
        self._intelligence_service = intelligence_service
        self._comparison_service = comparison_service
        self._innovation_service = innovation_service
        self.reports_cache: Dict[str, ResearchIntelligenceReport] = {}

    @property
    def intelligence_service(self):
        if self._intelligence_service is None:
            from backend.api.services.orchestrator import orchestrator
            self._intelligence_service = orchestrator
        return self._intelligence_service

    @property
    def comparison_service(self):
        if self._comparison_service is None:
            from backend.comparison.service import comparison_service
            self._comparison_service = comparison_service
        return self._comparison_service

    @property
    def innovation_service(self):
        if self._innovation_service is None:
            from backend.innovation.service import innovation_service
            self._innovation_service = innovation_service
        return self._innovation_service

    def generate_report(self, request: ReportGenerateRequest) -> ResearchIntelligenceReport:
        """Assembles, validates, and stores a structured research intelligence report."""
        report_id = f"PIQ-REP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        generated_at = datetime.now().strftime("%B %d, %Y - %H:%M UTC")

        # 1. Resolve Objective & Topic
        raw_text = (request.invention_description or request.query or "").strip()
        if not raw_text and request.session_id:
            from backend.copilot.session import copilot_session_manager
            sess = copilot_session_manager.get_session(request.session_id)
            if sess:
                raw_text = sess.current_query or ""
        
        if not raw_text and request.search_results:
            raw_text = "Prior-art research dataset analysis"

        if not raw_text:
            raw_text = "General Innovation Research"

        report_title = request.title or f"PatentIQ Research Intelligence: {raw_text[:50]}..."

        unavailable_sections: List[str] = []

        # 2. Resolve Retrieved Patents
        patents: List[Dict[str, Any]] = []
        if request.search_results:
            patents = request.search_results
        elif request.session_id:
            from backend.copilot.session import copilot_session_manager
            sess = copilot_session_manager.get_session(request.session_id)
            if sess and sess.retrieved_patents:
                patents = sess.retrieved_patents

        if not patents and (request.invention_description or request.query):
            search_query = request.query or request.invention_description or ""
            try:
                nl_res = self.intelligence_service.search_natural_language(
                    query=search_query,
                    top_k=request.top_k,
                    include_rag=False,
                    source_mode=request.source_mode
                )
                patents = nl_res.patents or []
            except Exception as e:
                logger.error(f"Retrieval error during report generation: {e}")
                patents = []

        # Filter by selected_patent_ids if supplied
        if request.selected_patent_ids and patents:
            selected_set = set(request.selected_patent_ids)
            filtered = [
                p for p in patents
                if p.get("publication_number") in selected_set or p.get("application_number") in selected_set
            ]
            if filtered:
                patents = filtered

        # 3. Query Understanding & Extracted Concepts
        tech_domain = "General Technology"
        extracted_concepts: List[str] = []
        try:
            q_und = self.intelligence_service.interpret_query(raw_text)
            tech_domain = getattr(q_und, "technology_domain", "General Technology") or "General Technology"
            extracted_concepts = getattr(q_und, "technical_concepts", []) or []
        except Exception:
            extracted_concepts = [w for w in raw_text.split() if len(w) > 4][:5]

        # 4. Provenance Tracking
        provenance = {
            "primary_source": f"Federated ({request.source_mode.capitalize()})",
            "total_retrieved": len(patents),
            "local_count": sum(1 for p in patents if p.get("provenance", {}).get("source_name") != "EPO European Publication Server"),
            "live_count": sum(1 for p in patents if p.get("provenance", {}).get("source_name") == "EPO European Publication Server"),
        }

        # 5. Prior-Art Landscape
        prior_art_landscape: List[PriorArtItem] = []
        detailed_summaries: List[DetailedPatentSummary] = []
        for p in patents[:15]:
            pub_id = p.get("publication_number") or p.get("application_number") or "Unknown ID"
            title = p.get("title") or "Patent Document"
            applicant = p.get("applicant") or p.get("applicant_name") or "Unknown Applicant"
            pub_date = p.get("publication_date") or None
            country = p.get("country") or (pub_id[:2] if len(pub_id) >= 2 and pub_id[:2].isalpha() else "IN")
            score = float(p.get("final_score") or p.get("semantic_score") or p.get("similarity_score") or 0.5)
            src_name = p.get("source") or p.get("provenance", {}).get("source_name") or "PatentIQ Corpus"

            pa_item = PriorArtItem(
                publication_number=pub_id,
                title=title,
                applicant=applicant,
                publication_date=pub_date,
                country=country,
                relevance_score=score,
                source=src_name,
                technical_concepts=extracted_concepts[:3]
            )
            prior_art_landscape.append(pa_item)

            # Detailed summary
            abstract = p.get("abstract") or "Abstract not provided in source record."
            claims = p.get("claims") or ""
            core_idea = abstract[:200] + "..." if len(abstract) > 200 else abstract
            detailed_summaries.append(DetailedPatentSummary(
                publication_number=pub_id,
                title=title,
                applicant=applicant,
                core_technical_idea=core_idea,
                problem_addressed=f"Addresses technical constraints within {tech_domain.lower()}.",
                proposed_approach=f"Describes specific mechanisms disclosed under publication {pub_id}.",
                relevance_to_objective=f"Shows conceptual overlap regarding {', '.join(extracted_concepts[:2]) if extracted_concepts else 'the core domain'}.",
                evidence_source=src_name,
                key_methods=[w for w in title.split() if len(w) > 4][:3]
            ))

        # 6. Patent Comparison (Feature 2)
        comparison_section: Optional[ComparisonSummary] = None
        if request.include_comparison:
            if request.comparison_results:
                cr = request.comparison_results
                comparison_section = ComparisonSummary(
                    compared_patents=cr.get("compared_patents", []),
                    shared_concepts=cr.get("shared_concepts", []),
                    distinct_concepts=cr.get("distinct_concepts", {}),
                    technical_differences=cr.get("technical_differences", []),
                    combination_gaps=cr.get("combination_gaps", [])
                )
            elif request.comparison_patents and len(request.comparison_patents) in (2, 3):
                try:
                    from backend.comparison.models import CompareRequest
                    c_resp = self.comparison_service.compare_patents(CompareRequest(patents=request.comparison_patents))
                    comparison_section = ComparisonSummary(
                        compared_patents=c_resp.compared_patents,
                        shared_concepts=c_resp.shared_concepts,
                        distinct_concepts=c_resp.distinct_concepts,
                        technical_differences=c_resp.technical_differences,
                        combination_gaps=c_resp.combination_gaps
                    )
                except Exception as e:
                    logger.warning(f"Comparison service fallback in report: {e}")
                    unavailable_sections.append("Patent Comparison")
            elif patents and len(patents) >= 2 and request.selected_patent_ids and len(request.selected_patent_ids) in (2, 3):
                try:
                    from backend.comparison.models import CompareRequest
                    c_resp = self.comparison_service.compare_patents(CompareRequest(patent_ids=request.selected_patent_ids))
                    comparison_section = ComparisonSummary(
                        compared_patents=c_resp.compared_patents,
                        shared_concepts=c_resp.shared_concepts,
                        distinct_concepts=c_resp.distinct_concepts,
                        technical_differences=c_resp.technical_differences,
                        combination_gaps=c_resp.combination_gaps
                    )
                except Exception as e:
                    logger.warning(f"Comparison resolution fallback in report: {e}")
                    unavailable_sections.append("Patent Comparison")
            else:
                unavailable_sections.append("Patent Comparison")
        else:
            unavailable_sections.append("Patent Comparison")

        # 7. Novelty Indicator (Deterministic)
        novelty_section: Optional[NoveltyIndicatorSection] = None
        if patents:
            from backend.intelligence.novelty_scoring import calculate_novelty_score
            q_und_dict = {"technology_domain": tech_domain, "key_concepts": extracted_concepts or [raw_text]}
            nov_data = calculate_novelty_score(patents, q_und_dict)
            novelty_section = NoveltyIndicatorSection(
                overall_novelty_score=nov_data.get("overall_novelty_score", 50),
                band=nov_data.get("band", "Moderate Differentiation"),
                explanation=nov_data.get("rationale") or "Automated prior-art similarity based on retrieved references.",
                disclaimer="This is an automated prior-art similarity indicator and is not a legal determination of patentability or novelty."
            )
        else:
            unavailable_sections.append("AI-Estimated Novelty Indicator")

        # 8. Concept Coverage Landscape (Deterministic)
        concept_coverage_items: List[ReportConceptCoverageItem] = []
        if patents and extracted_concepts:
            from backend.intelligence.innovation_gap import score_concept_coverage
            for conc in extracted_concepts:
                cov = score_concept_coverage(conc, patents)
                raw_score = float(cov.get("coverage_score", 50))
                # Normalize to 0.0 - 1.0 if returned as percentage 0-100
                norm_score = raw_score / 100.0 if raw_score > 1.0 else raw_score
                concept_coverage_items.append(ReportConceptCoverageItem(
                    concept=conc,
                    status=cov.get("coverage_band", "Moderately Represented"),
                    max_similarity=norm_score,
                    representative_patents=cov.get("representative_patents", [])
                ))
        else:
            unavailable_sections.append("Concept Coverage Landscape")

        # 9. Whitespace & Combination Gaps (Deterministic)
        combination_gap_items: List[ReportCombinationGapItem] = []
        if patents:
            from backend.intelligence.innovation_gap import detect_innovation_gaps
            gaps_data = detect_innovation_gaps(patents, {"technology_domain": tech_domain, "key_concepts": extracted_concepts or [raw_text]})
            for g in gaps_data:
                combination_gap_items.append(ReportCombinationGapItem(
                    gap_title=g.get("gap_title") or g.get("concept") or "Potential Pairwise Gap",
                    concept_pair=g.get("concept") or "Concept Pair",
                    joint_saturation=g.get("joint_saturation") or "Low",
                    rationale=g.get("rationale") or g.get("description") or "Limited pairwise co-occurrence in retrieved art.",
                    status=g.get("status") or "Potential Combination Gap"
                ))

        # 10. Innovation Refinement & Differentiation (Feature 3)
        diff_directions: List[ReportDifferentiationDirectionItem] = []
        res_questions: List[str] = []
        if request.include_innovation:
            if request.innovation_results:
                ir = request.innovation_results
                for d in ir.get("differentiation_directions", []):
                    diff_directions.append(ReportDifferentiationDirectionItem(**d))
                res_questions = ir.get("research_questions", [])
            elif raw_text:
                try:
                    from backend.innovation.models import InnovationAnalyzeRequest
                    ir_resp = self.innovation_service.analyze_innovation(InnovationAnalyzeRequest(
                        idea=raw_text,
                        source_mode=request.source_mode,
                        top_k=min(len(patents) or 5, 10),
                        comparison_context=request.comparison_results or ({"patents": request.comparison_patents} if request.comparison_patents else None)
                    ))
                    for d in ir_resp.differentiation_directions:
                        diff_directions.append(ReportDifferentiationDirectionItem(
                            direction=d.direction,
                            category=d.category,
                            evidence_gap_level=d.evidence_gap_level,
                            why_investigate=d.why_investigate,
                            related_concepts=d.related_concepts,
                            research_question=d.research_question,
                            linked_patent_ids=d.linked_patent_ids
                        ))
                    res_questions = ir_resp.research_questions
                except Exception as e:
                    logger.warning(f"Innovation refinement fallback in report: {e}")
                    unavailable_sections.append("Technical Differentiation Directions")
            else:
                unavailable_sections.append("Technical Differentiation Directions")
        else:
            unavailable_sections.append("Technical Differentiation Directions")

        # 11. Key Applicants & Distribution
        applicant_trends: List[ApplicantTrendItem] = []
        if patents:
            from collections import Counter
            counts = Counter([p.get("applicant") or p.get("applicant_name") or "Unknown" for p in patents if p.get("applicant") or p.get("applicant_name")])
            for app, count in counts.most_common(5):
                sample_pats = [p.get("publication_number") or p.get("application_number") for p in patents if (p.get("applicant") or p.get("applicant_name")) == app][:3]
                applicant_trends.append(ApplicantTrendItem(applicant=app, patent_count=count, sample_patents=[s for s in sample_pats if s]))
        else:
            unavailable_sections.append("Key Applicants & Technology Trends")

        # 12. Grounded Executive Summary Synthesis
        top_ids = [p.get("publication_number") or p.get("application_number") for p in patents[:3] if p.get("publication_number") or p.get("application_number")]
        nov_band = novelty_section.band if novelty_section else "Indeterminate"
        nov_score = novelty_section.overall_novelty_score if novelty_section else "N/A"

        exec_overview = (
            f"This research intelligence report evaluates the prior-art landscape for '{raw_text}'. "
            f"A total of {len(patents)} prior-art references were retrieved across {request.source_mode.capitalize()} sources. "
            f"The retrieved documents establish saturation around {', '.join(extracted_concepts[:3]) if extracted_concepts else 'primary technical concepts'}, "
            f"yielding an AI-Estimated Novelty Indicator of {nov_score}/100 ({nov_band})."
        )

        key_findings = [
            f"Identified {len(patents)} relevant patent documents matching the research objective.",
            f"Strongest prior-art representation observed in {', '.join(extracted_concepts[:2]) if extracted_concepts else 'core architectural methods'}.",
            f"Identified {len(combination_gap_items)} potential pairwise combination gaps for differentiated technical investigation."
        ]
        if comparison_section:
            key_findings.append(f"Structured comparison conducted across {len(comparison_section.compared_patents)} documents: shared concepts include {', '.join(comparison_section.shared_concepts[:2]) if comparison_section.shared_concepts else 'baseline methods'}.")

        exec_summary = ExecutiveSummary(
            overview=exec_overview,
            key_findings=key_findings,
            top_relevant_patents=top_ids,
            novelty_summary=f"Automated similarity scores reflect {nov_band.lower()} relative to evaluated prior art. This is not a legal novelty determination.",
            differentiation_summary=f"{len(diff_directions)} technical differentiation directions identified to diverge from prior-art saturation."
        )

        # 13. Research Objective & Methodology Scope
        research_objective = ResearchObjective(
            statement=raw_text,
            technical_domain=tech_domain,
            key_concepts=extracted_concepts
        )

        methodology = MethodologyScope(
            retrieval_strategy=f"Semantic and hybrid retrieval under {request.source_mode} mode",
            sources_searched=["Indian Patent Corpus (~115k records)"] + (["EPO European Publication Server"] if request.source_mode in ("hybrid", "live") else []),
            total_patents_evaluated=len(patents),
            scoring_framework="Cosine similarity on all-MiniLM-L6-v2 embeddings with BM25 fusion and canonical novelty scoring",
            limitations_summary=f"Bounded to indexed corpus ({provenance.get('local_count', 0)} local) and live API responses ({provenance.get('live_count', 0)} EPO)."
        )

        # 14. Limitations
        limitations = LimitationsSection(
            dataset_coverage="Corpus coverage includes cleaned Indian patent filings and European Patent Office publications. Does not constitute an exhaustive global search.",
            missing_data_notes=[
                "Certain legacy documents may contain truncated descriptions or OCR-derived text.",
                "Live EPO availability is subject to upstream server rate limits and network latency.",
                "Absence of representation in the retrieved set does not guarantee global absence of prior art."
            ],
            legal_boundaries="This report provides technical research insights and must not be used as a legal freedom-to-operate or patentability opinion."
        )

        # 15. Assemble Report Object
        report = ResearchIntelligenceReport(
            report_id=report_id,
            title=report_title,
            generated_at=generated_at,
            cover_page=CoverPageInfo(
                report_title=report_title,
                invention_topic=raw_text,
                report_id=report_id,
                generation_date=generated_at
            ),
            executive_summary=exec_summary,
            research_objective=research_objective,
            methodology=methodology,
            prior_art_landscape=prior_art_landscape,
            detailed_patent_summaries=detailed_summaries,
            patent_comparison=comparison_section,
            novelty_indicator=novelty_section,
            concept_coverage=concept_coverage_items,
            combination_gaps=combination_gap_items,
            differentiation_directions=diff_directions,
            research_questions=res_questions,
            applicant_trends=applicant_trends,
            limitations=limitations,
            disclaimer=MANDATORY_DISCLAIMER,
            provenance=provenance,
            unavailable_sections=sorted(list(set(unavailable_sections)))
        )

        # Cache in memory
        self.reports_cache[report_id] = report
        return report

    def get_report(self, report_id: str) -> Optional[ResearchIntelligenceReport]:
        """Retrieves a cached report by ID."""
        return self.reports_cache.get(report_id)

    def get_report_markdown(self, report_id: str) -> Optional[str]:
        """Renders report as Markdown."""
        report = self.get_report(report_id)
        if not report:
            return None
        return generate_markdown_report(report)

    def get_report_pdf(self, report_id: str) -> Optional[bytes]:
        """Renders report as PDF bytes."""
        report = self.get_report(report_id)
        if not report:
            return None
        return generate_pdf_report(report)

# Global singleton
report_service = ReportGenerationService()
