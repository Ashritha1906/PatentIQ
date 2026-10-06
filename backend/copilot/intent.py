import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from backend.copilot.models import CopilotIntent
from backend.copilot.context import CopilotSession

logger = logging.getLogger("CopilotIntent")

ORDINAL_MAP = {
    "first": 0, "1st": 0, "one": 0, "#1": 0, "patent 1": 0, "top 1": 0,
    "second": 1, "2nd": 1, "two": 1, "#2": 1, "patent 2": 1, "top 2": 1,
    "third": 2, "3rd": 2, "three": 2, "#3": 2, "patent 3": 2,
    "fourth": 3, "4th": 3, "four": 3, "#4": 3, "patent 4": 3,
    "fifth": 4, "5th": 4, "five": 4, "#5": 4, "patent 5": 4
}

def classify_intent(message: str, session: Optional[CopilotSession] = None) -> Tuple[CopilotIntent, Dict[str, Any]]:
    msg_clean = (message or "").strip()
    msg_lower = msg_clean.lower()
    
    details: Dict[str, Any] = {
        "raw_message": msg_clean,
        "referenced_indices": [],
        "patent_id_references": [],
        "entities": [],
        "technical_concepts": [],
        "domain": "GENERAL TECHNOLOGY",
        "action": "prior_art_search",
        "is_followup": False
    }

    if not msg_clean:
        return CopilotIntent.PRIOR_ART_SEARCH, details

    # Extract explicit patent identifiers
    id_matches = re.findall(r'\b(?:EP\s*\d+[A-Z0-9]*|\d+/[A-Z]+(?:NP)?/\d+|\d{12})\b', msg_clean, re.IGNORECASE)
    if id_matches:
        details["patent_id_references"] = [p.replace(" ", "").upper() for p in id_matches]

    # Check for ordinal references
    for word, idx in ORDINAL_MAP.items():
        if re.search(r'\b' + re.escape(word) + r'\b', msg_lower):
            if idx not in details["referenced_indices"]:
                details["referenced_indices"].append(idx)

    has_retrieved_context = bool(session and session.retrieved_patents)

    # 1. REPORT INTENT
    if "report" in msg_lower:
        details["action"] = "generate_report"
        return CopilotIntent.REPORT, details

    # 2. WHITESPACE INTENT
    if any(k in msg_lower for k in [
        "whitespace", "white space", "gaps", "gap analysis", "uncovered", 
        "not well covered", "missing concepts", "weakly represented", 
        "technology gap", "what areas are not covered", "concept coverage"
    ]):
        details["action"] = "analyze_whitespace"
        return CopilotIntent.WHITESPACE, details

    # 3. IMPROVE IDEA / DIFFERENTIATION INTENT
    if any(k in msg_lower for k in [
        "improve my idea", "differentiate", "differentiation", "more differentiated",
        "stand out", "avoid prior art", "make my idea novel", "is my idea different",
        "how is my idea different", "how can i differentiate", "novelty improvement"
    ]):
        details["action"] = "differentiate_idea"
        return CopilotIntent.IMPROVE_IDEA, details

    # 4. COMPARE INTENT
    if any(k in msg_lower for k in [
        "compare", "difference between", "differences between", "compare the",
        "versus", " vs ", " vs. ", "how do they compare", "how are they different"
    ]):
        details["action"] = "compare_patents"
        return CopilotIntent.COMPARE, details

    # 5. EXPLAIN INTENT
    if any(k in msg_lower for k in [
        "explain", "how does it work", "break down", "simplify", "simple words",
        "explain this patent", "explain like", "beginner", "plain english",
        "walk me through", "what does this patent do"
    ]):
        details["action"] = "explain_patent"
        return CopilotIntent.EXPLAIN, details

    # 6. SUMMARIZE INTENT
    if any(k in msg_lower for k in [
        "summarize", "summary of the patents", "overview of retrieved", 
        "recap the patents", "give me a summary", "brief synthesis"
    ]):
        details["action"] = "summarize_results"
        return CopilotIntent.SUMMARIZE, details

    # 7. FOLLOW UP INTENT
    is_short_question = len(msg_clean.split()) <= 8
    has_pronouns = any(p in msg_lower for p in ["it", "this", "that", "closest", "which one", "why", "second one", "first one"])
    is_inquiry_start = any(msg_lower.startswith(w) for w in ["why", "which", "does it", "is it", "what about", "how does", "can you"])

    if has_retrieved_context and (has_pronouns or is_inquiry_start or (is_short_question and "?" in msg_clean)):
        details["action"] = "answer_follow_up"
        details["is_followup"] = True
        return CopilotIntent.FOLLOW_UP, details

    # 8. PRIOR ART SEARCH (Default)
    details["action"] = "search_prior_art"
    return CopilotIntent.PRIOR_ART_SEARCH, details
