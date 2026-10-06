from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional
from backend.retrieval.query_model import (
    QueryIntent,
    PatentQuery,
    PatentSearchResult,
    NLSearchRequest,
    NLSearchResponse
)

class IdeaRequest(BaseModel):
    idea_text: str = Field(..., description="The description of the invention idea to analyze.")
    top_k: Optional[int] = Field(5, description="Number of top similar patents to retrieve.")
    domain_filter: Optional[str] = Field(None, description="Optional technology domain filter.")
    applicant_filter: Optional[str] = Field(None, description="Optional applicant/assignee filter.")

class SearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Natural language invention search query.")
    idea_text: Optional[str] = Field(None, description="Legacy field for invention idea text.")
    top_k: Optional[int] = Field(5, description="Number of top results to retrieve.")
    include_rag: Optional[bool] = Field(False, description="Whether to include Gemini RAG analysis.")
    domain_filter: Optional[str] = Field(None, description="Optional technology domain filter.")
    applicant_filter: Optional[str] = Field(None, description="Optional applicant/assignee filter.")

    @model_validator(mode="before")
    @classmethod
    def check_query_or_idea(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("query") and not data.get("idea_text"):
                raise ValueError("Either 'query' or 'idea_text' must be provided.")
        return data

class PatentIQResponse(BaseModel):
    user_idea: str = Field(..., description="The original user invention idea.")
    technology_domain: Dict[str, Any] = Field(..., description="Extracted technology domain and concepts.")
    similar_patents: List[Dict[str, Any]] = Field(..., description="List of semantically similar patents.")
    evidence_ranking: List[Dict[str, Any]] = Field(..., description="Detailed programmatic evidence ranking.")
    concept_clusters: Dict[str, Any] = Field(..., description="Unsupervised concept map and cluster landscape.")
    novelty_score: Dict[str, Any] = Field(..., description="Novelty score evaluation, classification, and explanation.")
    innovation_gaps: List[Dict[str, Any]] = Field(..., description="White-space or weakly represented concept gaps.")
    analysis: str = Field(..., description="Deep Gemini RAG comparative analysis report.")
    confidence_score: Dict[str, Any] = Field(..., description="Confidence and evidence quality assessment.")
