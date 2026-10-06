import os
import logging
from fastapi import APIRouter
from backend.retrieval.search_patents import get_retrieval_resources
from backend.llm.gemini_client import MOCK_LLM

logger = logging.getLogger("HealthRoute")
router = APIRouter()

@router.get("/health")
def health_check():
    """
    Returns system status checks for the application runtime, database, and LLM services.
    """
    status = {
        "status": "healthy",
        "database": "disconnected",
        "llm_mode": "mock" if MOCK_LLM else "live",
        "environment": {
            "db_path_exists": False
        }
    }
    
    # 1. Check ChromaDB
    db_path = "data/vectordb"
    if os.path.exists(db_path):
        status["environment"]["db_path_exists"] = True
        try:
            _, collection = get_retrieval_resources(db_path)
            # Fetch count to confirm read capability
            doc_count = collection.count()
            status["database"] = f"connected (count: {doc_count})"
        except Exception as e:
            logger.error(f"Health Check database connection error: {e}")
            status["status"] = "degraded"
            status["database"] = f"error: {str(e)}"
    else:
        status["status"] = "unhealthy"
        status["database"] = f"error: path {db_path} not found"
        
    return status
