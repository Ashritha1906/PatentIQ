import re
import logging
from typing import Dict, Any, List, Optional
from backend.copilot.context import CopilotSession

logger = logging.getLogger("CopilotResolver")

def resolve_target_patent(
    message: str,
    session: CopilotSession,
    intent_details: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Resolves the specific patent being asked about in the session context.
    Handles explicit IDs, ordinal references ('first', 'second'), and relative references ('closest').
    """
    if not session.retrieved_patents:
        return None

    msg_lower = (message or "").lower()

    # 1. Match by explicit patent ID or publication number
    for ref_id in intent_details.get("patent_id_references", []):
        ref_norm = re.sub(r'[^A-Za-z0-9]', '', ref_id).upper()
        for p in session.retrieved_patents:
            p_id = re.sub(r'[^A-Za-z0-9]', '', (
                p.get("publication_number") or 
                p.get("application_number") or 
                p.get("patent_id") or ""
            )).upper()
            if ref_norm in p_id or p_id in ref_norm:
                return p

    # 2. Match by referenced ordinal index (0 for first, 1 for second, etc.)
    indices = intent_details.get("referenced_indices", [])
    if indices:
        target_idx = indices[0]
        if 0 <= target_idx < len(session.retrieved_patents):
            return session.retrieved_patents[target_idx]

    # 3. Match relative references like 'closest', 'most relevant', 'top result'
    if any(k in msg_lower for k in ["closest", "most relevant", "top patent", "best match", "highest score"]):
        return session.retrieved_patents[0]

    # 4. Anaphora resolution: 'it', 'this', 'that', 'the patent'
    # Fall back to currently active selected patent in session, or index 0
    if session.selected_patent:
        return session.selected_patent

    return session.retrieved_patents[0]


def resolve_comparison_targets(
    message: str,
    session: CopilotSession,
    intent_details: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Resolves two patents to be compared.
    Defaults to the top 2 retrieved patents if available.
    """
    if not session.retrieved_patents:
        return []

    patents = session.retrieved_patents
    indices = intent_details.get("referenced_indices", [])

    # If user specified two distinct indices (e.g. 'first and third')
    if len(indices) >= 2:
        res = []
        for idx in indices[:2]:
            if 0 <= idx < len(patents):
                res.append(patents[idx])
        if len(res) == 2:
            return res

    # If user specifies 'it with the second', compare selected_patent with index 1
    msg_lower = (message or "").lower()
    if "with the" in msg_lower and indices and session.selected_patent:
        idx = indices[0]
        if 0 <= idx < len(patents) and patents[idx] != session.selected_patent:
            return [session.selected_patent, patents[idx]]

    # Default fallback: Top 2 patents
    return patents[:2]


def extract_specific_technical_inquiry(message: str) -> Optional[str]:
    """
    Extracts the technical entity or mechanism the user is asking about in a follow-up.
    e.g., 'does it use CNN?' -> 'CNN'
    'does it use deep learning?' -> 'deep learning'
    """
    msg = message.strip()
    match = re.search(r'(?:does it use|is it using|does this patent use|does patent [^\s]+ use|does it have)\s+([a-zA-Z0-9\s\-]+?)(?:\?|$|\.|\,)', msg, re.IGNORECASE)
    if match:
        tech = match.group(1).strip()
        if tech and tech.lower() not in {"a", "an", "the", "any", "some"}:
            return tech
    return None
