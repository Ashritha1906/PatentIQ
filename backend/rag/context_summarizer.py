import json
import logging
from backend.llm.gemini_client import generate_text

logger = logging.getLogger("ContextSummarizer")

SYSTEM_INSTRUCTION = (
    "You are a Senior Patent Analyst. Analyze the provided list of retrieved patents "
    "and summarize them at a conceptual level. Output your response ONLY as a valid, "
    "single-line JSON string. Do not wrap in markdown tags like ```json. The JSON must contain the keys: "
    "\"shared_concepts\" (list of strings), \"unique_concepts\" (list of strings), "
    "\"domains\" (list of strings), \"themes\" (list of strings), \"summary\" (string)."
)

def summarize_context(retrieved_patents):
    """
    Transforms retrieved patents into concept-level summaries by extracting shared/unique concepts,
    domains, common themes, and compiling a unified summary.
    """
    if not retrieved_patents:
        return {
            "shared_concepts": [],
            "unique_concepts": [],
            "domains": [],
            "themes": [],
            "summary": "No patents retrieved to summarize."
        }

    # Format retrieved patents for the prompt
    formatted_items = []
    for idx, pat in enumerate(retrieved_patents):
        formatted_items.append(
            f"Patent [{idx + 1}] ID: {pat['application_number']}\n"
            f"  Title: {pat['title']}\n"
            f"  Applicant: {pat['applicant_name']}\n"
            f"  Field: {pat['field_of_invention']} | IPC: {pat['classification_ipc']}\n"
            f"  Summary: {pat.get('patent_text', '')[:300]}...\n"
        )
    patents_text = "\n".join(formatted_items)

    prompt = (
        f"Analyze the following retrieved patents and extract concept-level summary details:\n\n"
        f"RETIEVED PATENTS:\n"
        f"{patents_text}\n\n"
        f"Extract core technical concepts, domains, common themes, unique features, "
        f"and output a compact evidence summary JSON."
    )

    try:
        response_text = generate_text(prompt, system_instruction=SYSTEM_INSTRUCTION)
        
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
        logger.error(f"Failed to parse context summarizer output: {e}. Raw response: {response_text if 'response_text' in locals() else 'None'}")
        
        # Build programmatic fallback
        all_concepts = []
        domains = []
        for pat in retrieved_patents:
            domains.append(pat["field_of_invention"])
            # Extract concepts from title keywords
            title_words = [w.capitalize() for w in pat["title"].split() if len(w) > 4]
            all_concepts.extend(title_words[:2])
            
        shared = list(set([c for c in all_concepts if all_concepts.count(c) > 1]))
        unique = list(set([c for c in all_concepts if all_concepts.count(c) == 1]))
        
        # Fallbacks if list is empty
        if not shared and unique:
            shared = unique[:1]
            unique = unique[1:]
            
        return {
            "shared_concepts": shared[:3] if shared else ["System Design"],
            "unique_concepts": unique[:5] if unique else ["Custom Implementation"],
            "domains": list(set(domains)),
            "themes": ["Information Extraction", "Processing Optimization"],
            "summary": "Concepts extracted programmatically due to parser constraint."
        }
