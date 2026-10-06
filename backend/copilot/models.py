from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CopilotIntent(str, Enum):
    PRIOR_ART_SEARCH = "PRIOR_ART_SEARCH"
    EXPLAIN = "EXPLAIN"
    COMPARE = "COMPARE"
    SUMMARIZE = "SUMMARIZE"
    WHITESPACE = "WHITESPACE"
    IMPROVE_IDEA = "IMPROVE_IDEA"
    FOLLOW_UP = "FOLLOW_UP"
    REPORT = "REPORT"

class CopilotTurn(BaseModel):
    role: str = Field(..., description="'user' or 'copilot'")
    content: str = Field(..., description="Message text content")
    intent: Optional[str] = Field(None, description="Classified intent for user turn")
    timestamp: float = Field(..., description="Turn epoch timestamp")

class ResearchContextSummary(BaseModel):
    current_query: Optional[str] = Field(None, description="Active research query/topic")
    intent: str = Field("IDLE", description="Last executed intent")
    patents_count: int = Field(0, description="Number of currently active retrieved patents in context")
    source_mode: str = Field("hybrid", description="Federated retrieval source mode: local, live, or hybrid")
    selected_patent_id: Optional[str] = Field(None, description="Currently selected or inspected patent identifier")
    technical_concepts: List[str] = Field(default_factory=list, description="Extracted core technical concepts")

class CopilotChatRequest(BaseModel):
    message: str = Field(..., description="User research question or natural language query")
    session_id: Optional[str] = Field(None, description="Optional UUID session token for context continuity")
    source_mode: Optional[str] = Field("hybrid", description="Patent source: 'local', 'live', or 'hybrid'")
    top_k: Optional[int] = Field(5, description="Number of patents to retrieve when performing search")

class CopilotChatResponse(BaseModel):
    session_id: str = Field(..., description="Canonical session UUID")
    message: str = Field(..., description="Conversational research response text")
    intent: str = Field(..., description="Classified intent for the query")
    query_understanding: Dict[str, Any] = Field(default_factory=dict, description="Structured query understanding details")
    patents: List[Dict[str, Any]] = Field(default_factory=list, description="Active or retrieved patents in this turn")
    selected_patent: Optional[Dict[str, Any]] = Field(None, description="Specific patent referenced or explained")
    analysis: Optional[Dict[str, Any]] = Field(None, description="Supplementary structured analysis (novelty, whitespace, comparison)")
    provenance: Optional[Dict[str, Any]] = Field(None, description="Provenance metadata for retrieved sources")
    research_context: ResearchContextSummary = Field(..., description="Current research context state")
    suggested_followups: List[str] = Field(default_factory=list, description="Contextual starter follow-up questions")
    disclaimer: str = Field(
        "This is an automated prior-art similarity indicator and is not a legal determination of patentability or novelty.",
        description="Mandatory patent intelligence disclaimer"
    )
