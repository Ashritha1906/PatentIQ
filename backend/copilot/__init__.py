from backend.copilot.models import (
    CopilotIntent,
    CopilotChatRequest,
    CopilotChatResponse,
    CopilotTurn,
    ResearchContextSummary
)
from backend.copilot.context import CopilotSession, SessionManager, session_manager
from backend.copilot.intent import classify_intent
from backend.copilot.resolver import resolve_target_patent, resolve_comparison_targets
from backend.copilot.service import CopilotService, copilot_service

__all__ = [
    "CopilotIntent",
    "CopilotChatRequest",
    "CopilotChatResponse",
    "CopilotTurn",
    "ResearchContextSummary",
    "CopilotSession",
    "SessionManager",
    "session_manager",
    "classify_intent",
    "resolve_target_patent",
    "resolve_comparison_targets",
    "CopilotService",
    "copilot_service",
]
