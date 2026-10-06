import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from backend.copilot.models import CopilotChatRequest, CopilotChatResponse
from backend.copilot.service import copilot_service
from backend.copilot.context import session_manager

router = APIRouter()
logger = logging.getLogger("CopilotRoute")

@router.post("/copilot/chat", response_model=CopilotChatResponse)
def copilot_chat(request: CopilotChatRequest):
    """
    Feature 1: AI Research Copilot conversational endpoint.
    Accepts natural-language queries, questions, or follow-ups and returns grounded research insights.
    """
    try:
        response = copilot_service.handle_chat(request)
        return response
    except Exception as e:
        logger.error(f"Copilot API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PatentIQ Copilot processing failed: {str(e)}"
        )

@router.get("/copilot/session/{session_id}")
def get_copilot_session(session_id: str):
    """
    Retrieves active research context and turn history for a session.
    """
    session = session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    return {
        "session_id": session.session_id,
        "summary": session.get_summary().model_dump(),
        "turns_count": len(session.turns),
        "turns": [t.model_dump() for t in session.turns]
    }

@router.delete("/copilot/session/{session_id}")
def delete_copilot_session(session_id: str):
    """
    Clears session memory and active research context.
    """
    deleted = session_manager.delete(session_id)
    return {"session_id": session_id, "deleted": deleted}
