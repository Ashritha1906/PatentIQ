from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator

class CompareRequest(BaseModel):
    patents: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of 2-3 full patent objects to compare directly"
    )
    patent_ids: Optional[List[str]] = Field(
        None, description="List of 2-3 patent identifiers (e.g. publication numbers) to compare"
    )
    session_id: Optional[str] = Field(
        None, description="Optional active session ID to resolve cached patent objects"
    )

    @model_validator(mode="after")
    def validate_selection_count(self):
        count = 0
        if self.patents:
            count = len(self.patents)
        elif self.patent_ids:
            count = len(self.patent_ids)
        else:
            raise ValueError("Must provide either 'patents' or 'patent_ids' to perform comparison.")

        if count < 2:
            raise ValueError("Select at least 2 patents to compare.")
        if count > 3:
            raise ValueError("Comparison is limited to 3 patents.")
        return self

class DeepDiveRequest(BaseModel):
    patent: Optional[Dict[str, Any]] = Field(
        None, description="Full patent object to deep dive into"
    )
    patent_id: Optional[str] = Field(
        None, description="Identifier of patent to deep dive into"
    )
    comparison_context: Optional[List[Dict[str, Any]]] = Field(
        None, description="Optional set of comparison patents to analyze relative distinction"
    )

    @model_validator(mode="after")
    def validate_target(self):
        if not self.patent and not self.patent_id:
            raise ValueError("Must provide either 'patent' object or 'patent_id'.")
        return self

class ComparisonMatrixDimension(BaseModel):
    dimension: str = Field(..., description="Feature or technical dimension being compared")
    source_evidence: str = Field(..., description="Primary evidence source: Abstract, Claims, Description, or Metadata")
    values: Dict[str, str] = Field(..., description="Mapping of patent_id to extracted value or 'Not available in retrieved evidence.'")

class TechnicalSimilarityScore(BaseModel):
    pair: List[str] = Field(..., description="Pair of patent identifiers compared")
    similarity_percentage: int = Field(..., description="AI-estimated technical similarity score [0-100]")
    explanation: str = Field(..., description="Analytical rationale for technical overlap")

class PatentComparisonResponse(BaseModel):
    patents: List[Dict[str, Any]] = Field(..., description="List of verified compared patent objects")
    summary: str = Field(..., description="AI-generated technical comparison overview grounded in evidence")
    matrix: List[ComparisonMatrixDimension] = Field(..., description="Structured multi-dimension comparison table")
    shared_concepts: List[str] = Field(default_factory=list, description="Concepts shared across multiple compared patents")
    distinct_concepts: Dict[str, List[str]] = Field(default_factory=dict, description="Concepts distinct to each patent within the selected set")
    key_differences: List[Dict[str, Any]] = Field(default_factory=list, description="Key architectural, algorithmic, or functional differences")
    combination_gaps: List[Dict[str, Any]] = Field(default_factory=list, description="Potential technology combinations less represented in the set")
    technical_similarities: List[TechnicalSimilarityScore] = Field(default_factory=list, description="Lightweight pairwise AI-estimated technical similarities")
    disclaimer: str = Field(
        "This comparison provides automated research intelligence and does NOT constitute a legal determination of infringement, patentability, validity, or freedom to operate.",
        description="Mandatory legal disclaimer"
    )

class DeepDiveResponse(BaseModel):
    patent_id: str = Field(..., description="Canonical patent publication number or identifier")
    title: str = Field(..., description="Patent title")
    summary: str = Field(..., description="Plain-language executive summary of the invention")
    problem_addressed: str = Field(..., description="Core technical problem addressed by the patent")
    proposed_solution: str = Field(..., description="Proposed technical solution and methodology")
    technical_workflow: str = Field(..., description="Step-by-step system execution workflow")
    technologies_methods: List[str] = Field(default_factory=list, description="Substantiated technologies, models, or algorithms mentioned")
    important_concepts: List[str] = Field(default_factory=list, description="Extracted core technical concepts")
    distinction_in_set: Optional[str] = Field(None, description="Technical distinction relative to comparison set")
    research_questions: List[str] = Field(default_factory=list, description="Forward-looking technical research questions for investigation")
    claim_focus: Optional[str] = Field(None, description="Technical focus of retrieved claims if present; otherwise explicit absence note")
    provenance: Optional[Dict[str, Any]] = Field(None, description="Corpus or database provenance")
    disclaimer: str = Field(
        "This deep dive provides automated technical analysis based on available patent text and does NOT constitute legal claim construction or a patentability opinion.",
        description="Mandatory legal disclaimer"
    )
