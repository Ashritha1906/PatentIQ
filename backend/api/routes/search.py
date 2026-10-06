import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from backend.api.services.dependencies import get_patent_service
from backend.api.services.orchestrator import PatentIntelligenceService

router = APIRouter()
logger = logging.getLogger("SearchRoute")

@router.post("/search")
def search_patents(
    request: Dict[str, Any],
    service: PatentIntelligenceService = Depends(get_patent_service)
):
    """
    Step 20: Natural language hybrid patent retrieval endpoint.
    Accepts:
      - Natural language query: {"query": "Find patents related to AI in retinal diagnosis...", "top_k": 10, "include_rag": true}
      - Legacy idea text: {"idea_text": "...", "top_k": 5}
    Returns:
      - NLSearchResponse dict when 'query' is provided.
      - List[Dict] when legacy 'idea_text' is provided.
    """
    try:
        query = request.get("query")
        idea_text = request.get("idea_text")
        top_k = request.get("top_k", 5)
        include_rag = bool(request.get("include_rag", False))
        domain_filter = request.get("domain_filter")
        applicant_filter = request.get("applicant_filter")

        # 1. Natural Language Query Mode (Phase 6A)
        if query is not None and str(query).strip():
            query_str = str(query).strip()
            logger.info(f"Search API: Processing natural language query '{query_str[:50]}'")
            source_mode = str(request.get("source_mode", "hybrid")).lower()
            nl_response = service.search_natural_language(
                query=query_str,
                top_k=top_k or 10,
                include_rag=include_rag,
                domain_filter=domain_filter,
                applicant_filter=applicant_filter,
                source_mode=source_mode
            )
            return nl_response.model_dump()

        # 2. Legacy Idea Text Mode (Backwards Compatibility)
        elif idea_text is not None:
            idea_str = str(idea_text)
            logger.info(f"Search API: Processing legacy idea text query '{idea_str[:50]}'")
            results = service.search_similar(
                query=idea_str,
                top_k=top_k or 5,
                domain_filter=domain_filter,
                applicant_filter=applicant_filter
            )
            return results

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid search request. Must provide either 'query' or 'idea_text'."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
