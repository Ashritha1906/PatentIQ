from fastapi import APIRouter, Depends, HTTPException
from backend.api.schemas.api_schemas import IdeaRequest, PatentIQResponse
from backend.api.services.dependencies import get_patent_service
from backend.api.services.orchestrator import PatentIntelligenceService

router = APIRouter()

@router.post("/analyze", response_model=PatentIQResponse)
def analyze_patent_idea(
    request: IdeaRequest,
    service: PatentIntelligenceService = Depends(get_patent_service)
):
    """
    Executes the full PatentIQ RAG analytical intelligence pipeline.
    Returns the complete structured patent report.
    """
    try:
        report = service.analyze_idea(
            idea_text=request.idea_text,
            top_k=request.top_k or 5,
            domain_filter=request.domain_filter,
            applicant_filter=request.applicant_filter
        )
        return report
    except ValueError as val_err:
        import logging
        logging.getLogger("AnalyzeRoute").warning(f"Validation failure in pipeline: {val_err}")
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        import logging
        logging.getLogger("AnalyzeRoute").error(f"Analyze API pipeline failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
