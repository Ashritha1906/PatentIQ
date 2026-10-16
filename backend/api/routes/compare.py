import logging
from fastapi import APIRouter, HTTPException
from backend.comparison.models import (
    CompareRequest,
    DeepDiveRequest,
    PatentComparisonResponse,
    DeepDiveResponse,
)
from backend.comparison.engine import comparison_engine

router = APIRouter()
logger = logging.getLogger("CompareRoute")

@router.post("/compare", response_model=PatentComparisonResponse)
def compare_patents(request: CompareRequest):
    """
    Feature 2: Structured multi-patent technical comparison.
    Accepts 2-3 patents or patent identifiers and returns a grounded comparative matrix,
    shared and distinct concepts, key technical differences, combination gaps, and pairwise similarities.
    """
    try:
        response = comparison_engine.compare(request)
        return response
    except ValueError as ve:
        logger.warning(f"Validation error in compare_patents: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Comparison API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PatentIQ Comparison processing failed: {str(e)}"
        )

@router.post("/compare/deep-dive", response_model=DeepDiveResponse)
def patent_deep_dive(request: DeepDiveRequest):
    """
    Feature 2: AI Deep Dive into an individual patent document.
    Returns plain-language summary, problem addressed, technical workflow,
    substantiated methods, concepts, research questions, and claim focus.
    """
    try:
        response = comparison_engine.deep_dive(request)
        return response
    except ValueError as ve:
        logger.warning(f"Validation error in patent_deep_dive: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Deep-dive API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PatentIQ Deep-Dive processing failed: {str(e)}"
        )