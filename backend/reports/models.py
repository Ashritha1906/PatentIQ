from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator
from datetime import datetime

class ReportGenerateRequest(BaseModel):
    title: Optional[str] = Field(None, description="Custom title for the research report")
    invention_description: Optional[str] = Field(None, description="Natural language description of the invention or research idea")
    query: Optional[str] = Field(None, description="Search query if different from invention description")
    source_mode: str = Field("hybrid", description="Retrieval source: hybrid, local, or live")
    top_k: int = Field(10, ge=1, le=50, description="Number of prior art patents to analyze")
    session_id: Optional[str] = Field(None, description="Optional Copilot or research session ID to pull context from")
    selected_patent_ids: Optional[List[str]] = Field(None, description="Specific patents to focus on or compare")
    include_comparison: bool = Field(True, description="Whether to include Feature 2 comparison section if available")
    include_innovation: bool = Field(True, description="Whether to include Feature 3 refinement section if available")
    comparison_patents: Optional[List[Dict[str, Any]]] = Field(None, description="Pre-selected 2-3 patents for comparison")
    comparison_results: Optional[Dict[str, Any]] = Field(None, description="Pre-computed Feature 2 comparison results")
    innovation_results: Optional[Dict[str, Any]] = Field(None, description="Pre-computed Feature 3 innovation analysis results")
    search_results: Optional[List[Dict[str, Any]]] = Field(None, description="Pre-retrieved patent results")

    @model_validator(mode="after")
    def validate_inputs(self):
        desc = (self.invention_description or "").strip()
        q = (self.query or "").strip()
        if not desc and not q and not self.search_results and not self.comparison_results and not self.innovation_results:
            raise ValueError("At least one research input (invention_description, query, or pre-computed results) must be provided.")
        return self

class CoverPageInfo(BaseModel):
    report_title: str
    invention_topic: str
    report_id: str
    generation_date: str
    organization: str = "PatentIQ Intelligence Engine"
    confidentiality: str = "Confidential Research Intelligence Document"

class ExecutiveSummary(BaseModel):
    overview: str
    key_findings: List[str]
    top_relevant_patents: List[str]
    novelty_summary: str
    differentiation_summary: str

class ResearchObjective(BaseModel):
    statement: str
    technical_domain: str
    key_concepts: List[str]

class MethodologyScope(BaseModel):
    retrieval_strategy: str
    sources_searched: List[str]
    total_patents_evaluated: int
    scoring_framework: str
    limitations_summary: str

class PriorArtItem(BaseModel):
    publication_number: str
    title: str
    applicant: str
    publication_date: Optional[str] = None
    country: Optional[str] = None
    relevance_score: float
    source: str
    technical_concepts: List[str] = []

class DetailedPatentSummary(BaseModel):
    publication_number: str
    title: str
    applicant: str
    core_technical_idea: str
    problem_addressed: str
    proposed_approach: str
    relevance_to_objective: str
    evidence_source: str
    key_methods: List[str] = []

class ComparisonSummary(BaseModel):
    compared_patents: List[str]
    shared_concepts: List[str]
    distinct_concepts: Dict[str, List[str]]
    technical_differences: List[str]
    combination_gaps: List[Dict[str, Any]] = []

class NoveltyIndicatorSection(BaseModel):
    overall_novelty_score: int
    band: str
    explanation: str
    disclaimer: str

class ReportConceptCoverageItem(BaseModel):
    concept: str
    status: str
    max_similarity: float
    representative_patents: List[str] = []

class ReportCombinationGapItem(BaseModel):
    gap_title: str
    concept_pair: str
    joint_saturation: str
    rationale: str
    status: str

class ReportDifferentiationDirectionItem(BaseModel):
    direction: str
    category: str
    evidence_gap_level: str
    why_investigate: str
    related_concepts: List[str]
    research_question: str
    linked_patent_ids: List[str] = []

class ApplicantTrendItem(BaseModel):
    applicant: str
    patent_count: int
    sample_patents: List[str]

class LimitationsSection(BaseModel):
    dataset_coverage: str
    missing_data_notes: List[str]
    legal_boundaries: str

class ResearchIntelligenceReport(BaseModel):
    report_id: str
    title: str
    generated_at: str
    cover_page: CoverPageInfo
    executive_summary: ExecutiveSummary
    research_objective: ResearchObjective
    methodology: MethodologyScope
    prior_art_landscape: List[PriorArtItem]
    detailed_patent_summaries: List[DetailedPatentSummary]
    patent_comparison: Optional[ComparisonSummary] = None
    novelty_indicator: Optional[NoveltyIndicatorSection] = None
    concept_coverage: List[ReportConceptCoverageItem] = []
    combination_gaps: List[ReportCombinationGapItem] = []
    differentiation_directions: List[ReportDifferentiationDirectionItem] = []
    research_questions: List[str] = []
    applicant_trends: List[ApplicantTrendItem] = []
    limitations: LimitationsSection
    disclaimer: str
    provenance: Dict[str, Any]
    unavailable_sections: List[str] = []
