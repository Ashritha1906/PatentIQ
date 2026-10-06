import json
import logging
import re
from typing import Dict, Any, Optional
from backend.llm.gemini_client import generate_text
from backend.retrieval.query_model import PatentQuery, QueryIntent
from backend.retrieval.query_expansion import expand_terms, build_search_phrases, validate_classification

logger = logging.getLogger("QueryUnderstanding")

# Legacy prompt for backwards compatibility with /analyze and /novelty routes
LEGACY_SYSTEM_INSTRUCTION = (
    "You are a Senior Patent Analytics AI. Analyze user invention ideas to extract "
    "retrieval parameters. Output your response ONLY as a valid, single-line JSON string. "
    "Do not wrap in markdown tags like ```json. The JSON must contain the keys: "
    "\"core_problem\" (string), \"technology_domain\" (string), \"key_concepts\" (list of strings), "
    "\"keywords\" (list of strings), \"optimized_query\" (string), \"metadata_hints\" (object with keys "
    "\"field_of_invention\" and \"applicant_name\")."
)

PLANNER_SYSTEM_INSTRUCTION = (
    "You are a Senior Patent Query Planner AI. Your task is to analyze natural language "
    "invention/research questions and formulate a structured patent search strategy. "
    "You must NOT invent patent numbers, classifications, or facts. Output ONLY valid JSON matching this schema: "
    "{\"original_query\": string, \"intent\": \"prior_art_search\"|\"patent_discovery\"|\"technology_landscape\"|\"patent_comparison\"|\"novelty_research\"|\"general_patent_question\", "
    "\"technical_concepts\": [string], \"expanded_terms\": [string], \"search_phrases\": [string], "
    "\"classification_candidates\": [string], \"entities\": [string], \"constraints\": {}, "
    "\"date_constraints\": {\"after\": int, \"before\": int} or null, \"applicant_constraints\": [string] or null, "
    "\"inventor_constraints\": [string] or null, \"confidence\": float}."
)

def understand_query(user_idea: str) -> Dict[str, Any]:
    """
    Analyzes raw user invention ideas and returns a structured dictionary of search parameters.
    Preserved for full backwards compatibility with legacy pipeline components.
    """
    prompt = (
        f"Analyze the following invention idea and generate retrieval parameters:\n"
        f"Idea: \"{user_idea}\"\n"
    )
    
    try:
        response_text = generate_text(prompt, system_instruction=LEGACY_SYSTEM_INSTRUCTION)
        
        # Clean up any potential markdown wraps
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        parsed_json = json.loads(cleaned_text)
        return parsed_json
        
    except Exception as e:
        logger.error(f"Failed to parse query understanding output: {e}. Raw response: {response_text if 'response_text' in locals() else 'None'}")
        return {
            "core_problem": f"Conceptual implementation of: {user_idea[:100]}",
            "technology_domain": "GENERAL ENGINEERING",
            "key_concepts": [user_idea[:30]],
            "keywords": user_idea.split()[:5],
            "optimized_query": user_idea[:200],
            "metadata_hints": {}
        }

def plan_patent_query(user_query: str) -> PatentQuery:
    """
    Step 4 & 5: Transforms an arbitrary natural language query into a structured PatentQuery strategy.
    Does not hallucinate patent numbers or facts. Enforces controlled intent enum and validated constraints.
    """
    cleaned_query = (user_query or "").strip()
    if not cleaned_query:
        return PatentQuery(
            original_query="",
            intent=QueryIntent.PATENT_DISCOVERY,
            confidence=0.0
        )

    # 1. Pre-extract explicit date constraints via regex
    q_lower = cleaned_query.lower()
    date_constraints: Optional[Dict[str, int]] = None
    after_match = re.search(r'(?:after|since|from|published after)\s+(\d{4})', q_lower)
    before_match = re.search(r'(?:before|until|to|prior to|published before)\s+(\d{4})', q_lower)
    if after_match or before_match:
        date_constraints = {}
        if after_match:
            date_constraints["after"] = int(after_match.group(1))
        if before_match:
            date_constraints["before"] = int(before_match.group(1))

    # 2. Pre-extract applicant/assignee constraints
    applicant_constraints = None
    app_match = re.search(r'(?:from|by|assigned to|applicant|company)\s+([A-Za-z0-9\s\.\-]+?)(?:patents|\b|$)', q_lower)
    if app_match:
        cand_app = app_match.group(1).strip()
        # Filter out generic stop words
        if cand_app and cand_app.lower() not in {"any", "all", "the", "a", "an", "recent", "new", "indian"}:
            applicant_constraints = [cand_app.upper()]

    # 3. Call Gemini Query Planner
    prompt = (
        f"You are a patent query planner. Formulate a structured patent search strategy for:\n"
        f"Query: \"{cleaned_query}\"\n"
    )

    try:
        response_text = generate_text(prompt, system_instruction=PLANNER_SYSTEM_INSTRUCTION)
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        data = json.loads(cleaned_text)
    except Exception as e:
        logger.warning(f"LLM query planner call failed or unparseable: {e}. Using deterministic fallback.")
        data = {}

    # 4. Resolve intent using controlled enum (default to patent_discovery per Step 3)
    raw_intent = data.get("intent", "").lower()
    try:
        intent = QueryIntent(raw_intent)
    except (ValueError, KeyError):
        # Heuristic intent detection if LLM did not provide a valid enum
        if any(w in q_lower for w in ["prior art", "existing patents", "infringe", "invalidity", "freedom to operate"]):
            intent = QueryIntent.PRIOR_ART_SEARCH
        elif any(w in q_lower for w in ["landscape", "trends", "state of the art", "industry"]):
            intent = QueryIntent.TECHNOLOGY_LANDSCAPE
        elif any(w in q_lower for w in ["compare", "difference", "vs", "versus"]):
            intent = QueryIntent.PATENT_COMPARISON
        elif any(w in q_lower for w in ["novel", "novelty", "is it new", "uniqueness"]):
            intent = QueryIntent.NOVELTY_RESEARCH
        elif any(w in q_lower for w in ["how to", "what is", "can i patent", "filing"]):
            intent = QueryIntent.GENERAL_PATENT_QUESTION
        else:
            intent = QueryIntent.PATENT_DISCOVERY

    # 5. Extract and normalize technical concepts
    technical_concepts = data.get("technical_concepts") or []
    if not technical_concepts:
        # Fallback to key substantive words from query
        words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_query)
                 if w.lower() not in {"find", "patents", "related", "with", "from", "using", "about", "what", "which", "after", "before", "show", "tell", "search"}]
        technical_concepts = words[:5] if words else [cleaned_query[:30]]

    # 6. Controlled query expansion
    expanded_terms = data.get("expanded_terms") or []
    if not expanded_terms:
        expanded_terms = expand_terms(technical_concepts)

    # 7. Build lexical search phrases
    search_phrases = data.get("search_phrases") or []
    if not search_phrases:
        search_phrases = build_search_phrases(technical_concepts, expanded_terms)

    # 8. Step 7: Classification Handling & Validation
    raw_classifications = data.get("classification_candidates") or []
    validated_classifications = []
    for cls_code in raw_classifications:
        is_valid, norm_code = validate_classification(cls_code)
        if is_valid and norm_code:
            validated_classifications.append(norm_code)
        else:
            logger.info(f"Omitted unvalidated or hallucinated classification: {cls_code}")

    # 9. Merge metadata constraints
    final_date_constraints = date_constraints or data.get("date_constraints")
    final_applicant_constraints = applicant_constraints or data.get("applicant_constraints")

    confidence = float(data.get("confidence", 0.95))
    confidence = max(0.1, min(1.0, confidence))

    return PatentQuery(
        original_query=cleaned_query,
        intent=intent,
        technical_concepts=technical_concepts,
        expanded_terms=expanded_terms,
        search_phrases=search_phrases,
        classification_candidates=validated_classifications,
        entities=data.get("entities") or (applicant_constraints or []),
        constraints=data.get("constraints") or {},
        date_constraints=final_date_constraints,
        applicant_constraints=final_applicant_constraints,
        inventor_constraints=data.get("inventor_constraints"),
        confidence=confidence
    )
