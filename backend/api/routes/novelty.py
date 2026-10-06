from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from backend.api.schemas.api_schemas import IdeaRequest
from backend.api.services.dependencies import get_patent_service
from backend.api.services.orchestrator import PatentIntelligenceService

router = APIRouter()

@router.post("/novelty", response_model=Dict[str, Any])
def evaluate_novelty(
    request: IdeaRequest,
    service: PatentIntelligenceService = Depends(get_patent_service)
):
    """
    Evaluates the novelty score and generates details for the user idea.
    """
    try:
        results = service.evaluate_novelty(
            idea_text=request.idea_text,
            top_k=request.top_k or 5,
            domain_filter=request.domain_filter,
            applicant_filter=request.applicant_filter
        )
        return results
    except Exception as e:
        import logging
        logging.getLogger("NoveltyRoute").error(f"Novelty API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Novelty evaluation failed: {str(e)}")
