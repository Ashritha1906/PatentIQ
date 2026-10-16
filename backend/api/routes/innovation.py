import logging
from fastapi import APIRouter, HTTPException
from backend.innovation.models import InnovationAnalyzeRequest, InnovationAnalysisResponse
from backend.innovation.service import innovation_service

router = APIRouter()
logger = logging.getLogger("InnovationRoute")

@router.post("/innovation/analyze", response_model=InnovationAnalysisResponse)
def analyze_innovation(request: InnovationAnalyzeRequest):
    """
    Feature 3: Innovation / Idea Refinement & Differentiation Engine.
    Analyzes an invention description against retrieved prior-art patents, evaluates
    semantic concept coverage across representation bands, computes canonical novelty,
    and surfaces structured technical differentiation directions and research questions.
    """
    try:
        response = innovation_service.analyze_innovation(request)
        return response
    except ValueError as ve:
        logger.warning(f"Validation error in analyze_innovation: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Innovation analysis API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PatentIQ Innovation Refinement failed: {str(e)}"
        )