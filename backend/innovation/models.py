from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator

class InnovationAnalyzeRequest(BaseModel):
    idea: str = Field(..., description="Natural language technical invention, system, or research description")
    source_mode: Optional[str] = Field("hybrid", description="Patent retrieval source: 'local', 'live', or 'hybrid'")
    top_k: Optional[int] = Field(5, description="Number of prior-art reference patents to retrieve")
    session_id: Optional[str] = Field(None, description="Optional active session identifier for context continuity")
    comparison_context: Optional[List[Dict[str, Any]]] = Field(None, description="Optional pre-existing comparison patents or insights")

    @model_validator(mode="after")
    def validate_idea_length(self):
        cleaned = (self.idea or "").strip()
        if not cleaned:
            raise ValueError("Idea description cannot be empty. Please provide a description of your invention or technical concept.")
        return self

class ConceptCoverageItem(BaseModel):
    concept: str = Field(..., description="Technical concept identified")
    coverage_score: float = Field(..., description="Representation score [0-100] across retrieved patents")
    coverage_band: str = Field(..., description="Representation status band")
    exact_phrase_present: bool = Field(False, description="Whether the verbatim literal phrase appears in retrieved patents")
    semantic_concept_present: bool = Field(False, description="Whether semantic equivalents or variants appear")
    containing_patents: List[str] = Field(default_factory=list, description="IDs of patents containing meaningful evidence")

class IdeaVsPriorArtItem(BaseModel):
    concept: str = Field(..., description="User idea concept")
    status: str = Field(..., description="Representation status in retrieved prior art")
    symbol: str = Field(..., description="Visual symbol: '✓' (Represented), '~' (Weak/Partial), '—' (Gap)")
    notes: str = Field(..., description="Concise analytical explanation of prior art evidence")

class DifferentiationDirection(BaseModel):
    direction_id: str = Field(..., description="Unique direction identifier")
    title: str = Field(..., description="Descriptive title of the technical differentiation direction")
    category: str = Field(..., description="Category: Technical Architecture, Data / Input, Processing Pipeline, AI / ML Methods, or System Combination")
    why_investigate: str = Field(..., description="Grounded explanation of why this direction is less represented in retrieved prior art")
    related_concepts: List[str] = Field(default_factory=list, description="Associated user and prior-art technical concepts")
    evidence_gap_level: str = Field(..., description="Qualitative gap level: HIGHER EVIDENCE GAP, MODERATE EVIDENCE GAP, WEAK EVIDENCE GAP, or INSUFFICIENT EVIDENCE")
    research_questions: List[str] = Field(default_factory=list, description="Empirical research questions for technical validation")
    related_patent_ids: List[str] = Field(default_factory=list, description="IDs of retrieved patents serving as benchmark prior art")

class InnovationAnalysisResponse(BaseModel):
    idea_summary: str = Field(..., description="Concise technical summary of user idea")
    technology_domain: str = Field(..., description="Identified technical field or domain")
    retrieved_patents: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved prior art patents")
    novelty_indicator: Dict[str, Any] = Field(..., description="Canonical AI-Estimated Novelty Indicator dictionary")
    concept_coverage: Dict[str, List[ConceptCoverageItem]] = Field(default_factory=dict, description="Concepts grouped by representation band")
    idea_vs_prior_art: List[IdeaVsPriorArtItem] = Field(default_factory=list, description="Direct mapping of user concepts to prior art evidence")
    combination_gaps: List[Dict[str, Any]] = Field(default_factory=list, description="Reused Phase 6A.1 combination whitespace gaps")
    differentiation_directions: List[DifferentiationDirection] = Field(default_factory=list, description="Technical differentiation directions")
    research_questions: List[str] = Field(default_factory=list, description="Forward-looking general research questions")
    provenance: Optional[Dict[str, Any]] = Field(None, description="Patent retrieval corpus provenance")
    insufficient_evidence: bool = Field(False, description="Flag indicating sparse or weak prior-art retrieval")
    disclaimer: str = Field(
        "This analysis is based on the retrieved prior-art set and is intended for research purposes. It is not a legal determination of patentability or novelty.",
        description="Mandatory legal disclaimer"
    )