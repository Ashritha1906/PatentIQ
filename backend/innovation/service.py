import re
import logging
from typing import Dict, Any, List, Optional
from backend.innovation.models import (
    InnovationAnalyzeRequest,
    ConceptCoverageItem,
    IdeaVsPriorArtItem,
    DifferentiationDirection,
    InnovationAnalysisResponse,
)
from backend.api.services.dependencies import get_patent_service
from backend.intelligence.innovation_gap import (
    score_concept_coverage,
    get_coverage_band,
    detect_innovation_gaps,
)
from backend.intelligence.novelty_scoring import calculate_novelty_score, NOVELTY_DISCLAIMER
from backend.llm.gemini_client import generate_text

logger = logging.getLogger("InnovationRefinement")

SYSTEM_INNOVATION_INSTRUCTION = (
    "You are the PatentIQ Innovation Research Analyst.\n"
    "Your task is to help users explore technical differentiation directions based on their innovation and the retrieved prior-art evidence.\n"
    "Use only the provided user idea, retrieved patent evidence, concept coverage, whitespace analysis, combination-gap analysis, and comparison context.\n"
    "Do not invent patent facts.\n"
    "Do not claim that an idea is globally novel.\n"
    "Do not claim that an idea is patentable.\n"
    "Do not claim that no patent covers a concept.\n"
    "An evidence gap means that the concept or combination has limited representation within the retrieved prior-art set. It does not prove global novelty.\n"
    "Suggest technically meaningful research directions.\n"
    "Every recommendation should be traceable to the available evidence.\n"
    "Use language such as:\n"
    "'Based on the retrieved prior-art set...'\n"
    "'may be worth investigating...'\n"
    "'appears less represented...'\n"
    "'could be explored...'\n"
    "Never provide legal conclusions."
)

class InnovationRefinementService:
    """
    Feature 3: Innovation / Idea Refinement & Differentiation Engine.
    Orchestrates existing PatentIQ retrieval, concept coverage, novelty scoring,
    and combination-gap analysis to synthesize actionable technical research directions.
    """

    def __init__(self, intelligence_service=None):
        self._intelligence_service = intelligence_service

    @property
    def intelligence_service(self):
        if self._intelligence_service is None:
            self._intelligence_service = get_patent_service()
        return self._intelligence_service

    def analyze_innovation(self, request: InnovationAnalyzeRequest) -> InnovationAnalysisResponse:
        cleaned_idea = request.idea.strip()
        if len(cleaned_idea) < 15:
            # Short / insufficient idea input handling
            return InnovationAnalysisResponse(
                idea_summary=cleaned_idea,
                technology_domain="GENERAL TECHNOLOGY",
                retrieved_patents=[],
                novelty_indicator={
                    "score": 0,
                    "novelty_score": 0,
                    "overall_novelty_score": 0,
                    "indicator_name": "AI-Estimated Novelty Indicator",
                    "band": "Insufficient Input",
                    "disclaimer": NOVELTY_DISCLAIMER,
                    "explanation": "PatentIQ requires a more detailed technical description to perform a reliable differentiation assessment.",
                    "breakdown": {"similarity_overlap": 0.0, "concept_uniqueness": 0.0, "domain_saturation": 0.0}
                },
                concept_coverage={},
                idea_vs_prior_art=[],
                combination_gaps=[],
                differentiation_directions=[],
                research_questions=[
                    "What specific inputs and data modalities does your system process?",
                    "What algorithms or models perform core decision-making?",
                    "What output or control signals are generated?"
                ],
                insufficient_evidence=True,
                disclaimer=NOVELTY_DISCLAIMER
            )

        # 1. Retrieve prior-art context using existing PatentIQ pipeline
        try:
            context = self.intelligence_service._retrieve_context(
                idea_text=cleaned_idea,
                top_k=request.top_k or 5
            )
            retrieved_patents = context.get("retrieved_patents", [])
            query_understanding = context.get("query_understanding", {})
        except Exception as e:
            logger.error(f"Retrieval failure in innovation analysis: {e}")
            retrieved_patents = []
            query_understanding = {
                "technology_domain": "GENERAL TECHNOLOGY",
                "keywords": [w for w in re.findall(r"\b[a-zA-Z]{4,}\b", cleaned_idea.lower()) if len(w) > 3][:6],
                "core_concepts": []
            }

        # Merge comparison context if provided from Feature 2
        if request.comparison_context:
            existing_ids = {p.get("publication_number") or p.get("application_number") for p in retrieved_patents}
            for cp in request.comparison_context:
                cpid = cp.get("publication_number") or cp.get("application_number")
                if cpid not in existing_ids:
                    retrieved_patents.append(cp)
                    existing_ids.add(cpid)

        # Handle zero or weak retrieval evidence
        if not retrieved_patents:
            return InnovationAnalysisResponse(
                idea_summary=cleaned_idea[:200],
                technology_domain=query_understanding.get("technology_domain", "GENERAL TECHNOLOGY"),
                retrieved_patents=[],
                novelty_indicator={
                    "score": 0,
                    "novelty_score": 0,
                    "overall_novelty_score": 0,
                    "indicator_name": "AI-Estimated Novelty Indicator",
                    "band": "Insufficient Evidence",
                    "disclaimer": NOVELTY_DISCLAIMER,
                    "explanation": "PatentIQ does not have enough relevant prior-art evidence in the active index to make a reliable differentiation assessment.",
                    "breakdown": {"similarity_overlap": 0.0, "concept_uniqueness": 0.0, "domain_saturation": 0.0}
                },
                concept_coverage={},
                idea_vs_prior_art=[],
                combination_gaps=[],
                differentiation_directions=[],
                research_questions=[
                    "Try broadening the technical terminology in your search.",
                    "Verify if synonyms exist for core components in patent classifications."
                ],
                insufficient_evidence=True,
                disclaimer=NOVELTY_DISCLAIMER
            )

        # 2. Existing Novelty Indicator (Programmatic & Canonical)
        novelty_data = calculate_novelty_score(retrieved_patents, query_understanding)

        # 3. Existing Concept Coverage Evaluation
        concepts_to_evaluate = []
        raw_keywords = query_understanding.get("keywords", [])
        raw_core = query_understanding.get("core_concepts", [])
        for c in raw_keywords + raw_core:
            clean_c = str(c).strip().title()
            if len(clean_c) > 2 and clean_c not in concepts_to_evaluate:
                concepts_to_evaluate.append(clean_c)

        # Fallback if query understanding returned few keywords
        if len(concepts_to_evaluate) < 3:
            extracted_words = re.findall(r"\b[a-zA-Z]{4,}\b", cleaned_idea.lower())
            stopwords = {"system", "method", "using", "with", "that", "this", "from", "have", "been", "which", "their"}
            for w in extracted_words:
                if w not in stopwords and w.title() not in concepts_to_evaluate:
                    concepts_to_evaluate.append(w.title())
                if len(concepts_to_evaluate) >= 6:
                    break

        grouped_coverage: Dict[str, List[ConceptCoverageItem]] = {
            "strongly_represented": [],
            "moderately_represented": [],
            "weakly_represented": [],
            "minimally_represented": [],
            "no_meaningful_evidence": []
        }
        idea_vs_prior_art: List[IdeaVsPriorArtItem] = []

        for concept in concepts_to_evaluate:
            cov = score_concept_coverage(concept, retrieved_patents)
            item = ConceptCoverageItem(
                concept=concept,
                coverage_score=cov["coverage_score"],
                coverage_band=cov["coverage_band"],
                exact_phrase_present=cov["exact_phrase_present"],
                semantic_concept_present=cov["semantic_concept_present"],
                containing_patents=cov.get("containing_patents", [])
            )
            score = cov["coverage_score"]
            if score >= 80:
                grouped_coverage["strongly_represented"].append(item)
                symbol = "?"
                notes = "Strong prior art representation in retrieved set."
            elif score >= 50:
                grouped_coverage["moderately_represented"].append(item)
                symbol = "?"
                notes = "Substantial conceptual coverage identified across patents."
            elif score >= 20:
                grouped_coverage["weakly_represented"].append(item)
                symbol = "~"
                notes = "Partial or peripheral coverage; possible differentiation opportunity."
            elif score >= 1:
                grouped_coverage["minimally_represented"].append(item)
                symbol = "~"
                notes = "Sparse prior art mention; less represented in retrieved set."
            else:
                grouped_coverage["no_meaningful_evidence"].append(item)
                symbol = "?"
                notes = "No meaningful evidence found in retrieved prior-art set."

            idea_vs_prior_art.append(IdeaVsPriorArtItem(
                concept=concept,
                status=cov["coverage_band"],
                symbol=symbol,
                notes=notes
            ))

        # 4. Existing Combination-Gap Analyzer (Reuse Phase 6A.1)
        raw_gaps = detect_innovation_gaps(retrieved_patents, query_understanding)
        combination_gaps = []
        for g in raw_gaps:
            combination_gaps.append({
                "gap_type": g.get("gap_type", "POTENTIAL_COMBINATION_GAP"),
                "concept": g.get("concept", "Technical Parameter"),
                "description": f"Within the retrieved prior-art set, the combination of {g.get('concept', 'identified elements')} appears less represented.",
                "investigation_suggestion": g.get("suggestion", "Explore complementary integration of these components."),
                "confidence": g.get("confidence", "MEDIUM")
            })

        # 5. Formulate Technical Differentiation Directions
        differentiation_directions: List[DifferentiationDirection] = []
        dir_counter = 1

        # A. System Combination Direction from combination gaps
        if combination_gaps:
            top_gap = combination_gaps[0]
            differentiation_directions.append(DifferentiationDirection(
                direction_id=f"DIR-{dir_counter}",
                title=f"Synergistic Integration: {top_gap['concept']}",
                category="System Combination",
                why_investigate=f"Within the retrieved prior-art set, the joint implementation of {top_gap['concept']} appears less represented than individual components.",
                related_concepts=[top_gap["concept"]],
                evidence_gap_level="HIGHER EVIDENCE GAP",
                research_questions=[
                    f"Does combining these elements provide demonstrable latency or accuracy advantages over existing approaches?",
                    "What specific communication or architectural protocol bridges these subsystems?"
                ],
                related_patent_ids=[p.get("application_number") or p.get("publication_number") or "Patent" for p in retrieved_patents[:2]]
            ))
            dir_counter += 1

        # B. Directions based on Weak / Minimal Concepts
        weak_or_minimal = grouped_coverage["weakly_represented"] + grouped_coverage["minimally_represented"] + grouped_coverage["no_meaningful_evidence"]
        categories = ["Technical Architecture", "Data / Input", "Processing Pipeline", "AI / ML Methods"]

        for i, c_item in enumerate(weak_or_minimal[:3]):
            cat = categories[i % len(categories)]
            gap_level = "HIGHER EVIDENCE GAP" if c_item.coverage_score == 0 else "MODERATE EVIDENCE GAP"
            differentiation_directions.append(DifferentiationDirection(
                direction_id=f"DIR-{dir_counter}",
                title=f"Specialized {cat} Enhancement: {c_item.concept}",
                category=cat,
                why_investigate=f"Concept '{c_item.concept}' exhibits {c_item.coverage_band.lower()} in the retrieved prior-art set ({c_item.coverage_score}% coverage). Investigating specialized implementations here may offer meaningful technical contrast.",
                related_concepts=[c_item.concept],
                evidence_gap_level=gap_level,
                research_questions=[
                    f"How does incorporating '{c_item.concept}' solve specific operational bottlenecks present in earlier patents?",
                    f"What empirical metrics benchmark this approach against the baseline methods of {retrieved_patents[0].get('title', 'retrieved prior art')}?"
                ],
                related_patent_ids=[p.get("application_number") or p.get("publication_number") or "Patent" for p in retrieved_patents[:2]]
            ))
            dir_counter += 1

        # Ensure at least 2 structured directions exist
        if len(differentiation_directions) < 2 and retrieved_patents:
            differentiation_directions.append(DifferentiationDirection(
                direction_id=f"DIR-{dir_counter}",
                title="Telemetry & Workflow Optimization",
                category="Processing Pipeline",
                why_investigate="Prior-art documents predominantly focus on batch computation. Designing an optimized stream pipeline represents a potential differentiation path.",
                related_concepts=concepts_to_evaluate[:2],
                evidence_gap_level="WEAK EVIDENCE GAP",
                research_questions=[
                    "What latency trade-offs emerge when shifting from batch evaluation to real-time verification?",
                    "Can edge inference constraints be satisfied without accuracy loss?"
                ],
                related_patent_ids=[retrieved_patents[0].get("application_number") or "Patent"]
            ))

        # 6. General Research Questions
        general_questions = [
            f"What specific training datasets and calibration protocols distinguish your pipeline in {query_understanding.get('technology_domain', 'this domain')}?",
            "What runtime hardware constraints or throughput limitations are unaddressed by the retrieved patents?",
            "How do your failure-mode mitigation mechanisms compare with existing published disclosures?"
        ]

        # Extract summary
        domain = query_understanding.get("technology_domain", "GENERAL TECHNOLOGY")
        idea_summary = cleaned_idea[:160] + "..." if len(cleaned_idea) > 160 else cleaned_idea

        provenance = retrieved_patents[0].get("provenance") if (retrieved_patents and retrieved_patents[0].get("provenance")) else {
            "source": request.source_mode.upper() if request.source_mode else "HYBRID",
            "count": len(retrieved_patents),
            "confidence": "HIGH"
        }

        return InnovationAnalysisResponse(
            idea_summary=idea_summary,
            technology_domain=domain,
            retrieved_patents=retrieved_patents,
            novelty_indicator=novelty_data,
            concept_coverage=grouped_coverage,
            idea_vs_prior_art=idea_vs_prior_art,
            combination_gaps=combination_gaps,
            differentiation_directions=differentiation_directions,
            research_questions=general_questions,
            provenance=provenance,
            insufficient_evidence=False,
            disclaimer=NOVELTY_DISCLAIMER
        )

innovation_service = InnovationRefinementService()
