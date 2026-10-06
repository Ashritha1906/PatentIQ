from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QueryIntent(str, Enum):
    PRIOR_ART_SEARCH = "prior_art_search"
    PATENT_DISCOVERY = "patent_discovery"
    TECHNOLOGY_LANDSCAPE = "technology_landscape"
    PATENT_COMPARISON = "patent_comparison"
    NOVELTY_RESEARCH = "novelty_research"
    GENERAL_PATENT_QUESTION = "general_patent_question"

class PatentQuery(BaseModel):
    original_query: str = Field(..., description="The raw natural language query provided by the user.")
    intent: QueryIntent = Field(default=QueryIntent.PATENT_DISCOVERY, description="Controlled intent classification.")
    technical_concepts: List[str] = Field(default_factory=list, description="Key technical concepts extracted from the query.")
    expanded_terms: List[str] = Field(default_factory=list, description="Controlled domain synonyms and expanded keywords.")
    search_phrases: List[str] = Field(default_factory=list, description="Multi-word Boolean/lexical search phrases.")
    classification_candidates: List[str] = Field(default_factory=list, description="Candidate IPC/CPC classification codes.")
    entities: List[str] = Field(default_factory=list, description="Named entities, organizations, or components.")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="General constraint filters.")
    date_constraints: Optional[Dict[str, Any]] = Field(default=None, description="Date boundaries, e.g. after/before year.")
    applicant_constraints: Optional[List[str]] = Field(default=None, description="Specific applicant/assignee filters.")
    inventor_constraints: Optional[List[str]] = Field(default=None, description="Specific inventor filters.")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score for the query interpretation.")

class PatentSearchResult(BaseModel):
    patent_id: str = Field(..., description="Unique patent identifier in PatentIQ.")
    publication_number: str = Field(..., description="Canonical publication or application number.")
    title: str = Field(..., description="Title of the patent.")
    abstract: Optional[str] = Field(default=None, description="Patent abstract or descriptive summary.")
    applicant: Optional[str] = Field(default=None, description="Applicant or assignee organization.")
    inventors: Optional[List[str]] = Field(default=None, description="List of named inventors if available.")
    publication_date: Optional[str] = Field(default=None, description="Publication date string.")
    country: Optional[str] = Field(default="IN", description="Two-letter ISO country code.")
    document_number: Optional[str] = Field(default=None, description="Canonical document number.")
    kind_code: Optional[str] = Field(default="A", description="Publication kind code.")
    classification: Optional[str] = Field(default=None, description="IPC/CPC classification code.")
    semantic_score: float = Field(default=0.0, description="Normalized semantic similarity score [0.0 - 1.0].")
    keyword_score: float = Field(default=0.0, description="Normalized keyword relevance score [0.0 - 1.0].")
    final_score: float = Field(default=0.0, description="Composite hybrid relevance score [0.0 - 1.0].")
    ranking_reasons: List[str] = Field(default_factory=list, description="Human-readable, explainable ranking factors.")
    source: str = Field(default="PatentIQ Corpus", description="Corpus or origin database of the patent.")
    source_url: Optional[str] = Field(default=None, description="Direct URL or reference link to the official patent record.")

class NLSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language invention or patent search query.")
    top_k: Optional[int] = Field(default=10, description="Number of top relevant patents to return.")
    include_rag: Optional[bool] = Field(default=False, description="Whether to invoke Gemini RAG for executive analysis.")
    domain_filter: Optional[str] = Field(default=None, description="Optional manual domain filter override.")
    applicant_filter: Optional[str] = Field(default=None, description="Optional manual applicant filter override.")
    source_mode: Optional[str] = Field(default="hybrid", description="Retrieval source mode: 'local', 'live', or 'hybrid'. Defaults to 'hybrid'.")

class NLSearchResponse(BaseModel):
    query: str = Field(..., description="Original user query.")
    interpreted_query: PatentQuery = Field(..., description="Structured interpretation of the user query.")
    search_strategy: Dict[str, Any] = Field(..., description="Summary of retrieval parameters and weights applied.")
    total_results: int = Field(..., description="Number of retrieved deduplicated results.")
    results: List[PatentSearchResult] = Field(..., description="Ranked list of patent candidates.")
    ranking_information: Dict[str, Any] = Field(..., description="Scoring breakdown and normalization parameters.")
    source_metadata: Dict[str, Any] = Field(..., description="Information regarding the underlying indexed patent dataset.")
    rag_answer: Optional[str] = Field(default=None, description="Optional RAG synthesized comparative answer.")
    confidence_message: Optional[str] = Field(default=None, description="Confidence indicator or guidance when matches are weak.")
    source_mode: Optional[str] = Field(default="hybrid", description="Retrieval source mode applied.")
    provenance_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Federated retrieval provenance metadata (counts, providers, fair-use).")
