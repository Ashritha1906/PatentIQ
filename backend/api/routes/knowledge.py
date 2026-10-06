import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.knowledge_expansion.sync_manager import SyncManager
from backend.knowledge_expansion.scheduler import SyncScheduler
from backend.knowledge_expansion.authentication import verify_auth

logger = logging.getLogger("KnowledgeRouter")
router = APIRouter()
sync_manager = SyncManager()
scheduler = SyncScheduler()

class SyncRequest(BaseModel):
    keyword: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_results: Optional[int] = 10

class ScheduleRequest(BaseModel):
    mode: str  # manual, daily, weekly, monthly

@router.get("/status", response_model=Dict[str, Any])
def get_knowledge_status():
    """
    Exposes metrics for the Knowledge Ingestion dashboard:
    Dataset size, active version, last runs, next scheduled check, and API status.
    """
    try:
        history = sync_manager.get_version_history()
        current_version = history[-1] if history else {}
        
        # Read scheduler settings
        sched_config = scheduler.get_config()
        
        # Verify Lens API status
        api_verified = verify_auth()
        
        # Get live database metrics
        total_vectors = 0
        try:
            from backend.retrieval.search_patents import get_retrieval_resources
            _, collection = get_retrieval_resources(sync_manager.db_path)
            total_vectors = collection.count()
        except Exception as e:
            logger.error(f"Failed to fetch collection count for status: {e}")
            
        return {
            "current_dataset_size": total_vectors,
            "current_version": current_version.get("version_id", "v1"),
            "last_sync": current_version.get("timestamp"),
            "next_sync": sched_config.get("next_sync"),
            "scheduler_mode": sched_config.get("mode", "manual"),
            "api_status": "ONLINE" if api_verified else "OFFLINE",
            "version_history": history
        }
    except Exception as e:
        logger.error(f"Status endpoint failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync", response_model=Dict[str, Any])
def trigger_manual_sync(req: SyncRequest):
    """
    Manually triggers an incremental synchronization job with optional query search filters.
    """
    try:
        # Construct search query DSL based on filters
        query_dsl: Dict[str, Any] = {}
        
        if req.start_date or req.end_date:
            start = req.start_date or "1970-01-01"
            end = req.end_date or "2030-01-01"
            query_dsl = {
                "range": {
                    "date_published": {
                        "gte": start,
                        "lte": end
                    }
                }
            }
        elif req.keyword:
            query_dsl = {
                "query_string": {
                    "query": req.keyword
                }
            }
        else:
            # Match recent publications if no criteria provided
            query_dsl = {
                "match_all": {}
            }

        logger.info(f"Manual sync triggered with query: {query_dsl} (Limit: {req.max_results})")
        stats = sync_manager.sync_latest_patents(
            query_dsl=query_dsl,
            max_results=req.max_results,
            source="Manual Sync API"
        )
        
        if stats.get("status") == "failed":
            raise HTTPException(status_code=400, detail=stats.get("error"))
            
        return stats
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule", response_model=Dict[str, Any])
def update_sync_schedule(req: ScheduleRequest):
    """
    Updates the periodic scheduler mode (e.g. Daily, Weekly, Monthly, or Manual).
    """
    try:
        config = scheduler.set_schedule(req.mode)
        return config
    except Exception as e:
        logger.error(f"Schedule update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit", response_model=Dict[str, Any])
def run_db_integrity_audit():
    """
    Performs verification audits on dimensions, null parameters, and collection status.
    """
    try:
        audit_res = sync_manager.run_database_audit()
        return audit_res
    except Exception as e:
        logger.error(f"Audit endpoint failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))
