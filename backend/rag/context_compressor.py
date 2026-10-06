import re
import logging

logger = logging.getLogger("ContextCompressor")

def clean_patent_text(text):
    """
    Strips standard legal boilerplate and redundancies to compress the text block.
    """
    if not text:
        return ""
    
    # Strip common legal phrases
    phrases_to_remove = [
        r"(?i)the present invention relates to",
        r"(?i)it is an object of the invention to",
        r"(?i)exemplary embodiments of the invention",
        r"(?i)according to one aspect of the invention"
    ]
    
    cleaned = text
    for phrase in phrases_to_remove:
        cleaned = re.sub(phrase, "", cleaned)
        
    # Remove excessive newlines/spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def compress_context(retrieved_patents):
    """
    Compresses a list of retrieved patent objects into a dense, token-efficient summary block.
    """
    compressed_items = []
    
    for idx, pat in enumerate(retrieved_patents):
        app_num = pat["application_number"]
        title = pat["title"]
        field = pat["field_of_invention"]
        ipc = pat["classification_ipc"]
        applicant = pat["applicant_name"]
        
        # Clean and extract first 250 characters of description for token-saving brief
        raw_text = pat.get("patent_text", "")
        cleaned_body = clean_patent_text(raw_text)
        
        # Keep only the first 2-3 sentences or 250 chars of cleaned body
        sentences = re.split(r'(?<=[.!?])\s+', cleaned_body)
        summary_body = " ".join(sentences[:3]) if sentences else cleaned_body[:250]
        if len(summary_body) > 300:
            summary_body = summary_body[:297] + "..."
            
        brief = (
            f"[{idx + 1}] Patent ID: {app_num}\n"
            f"    Title: {title}\n"
            f"    Applicant: {applicant}\n"
            f"    Field: {field} | IPC: {ipc}\n"
            f"    Brief: {summary_body}\n"
        )
        compressed_items.append(brief)
        
    compressed_block = "\n".join(compressed_items)
    token_saving_est = len(compressed_block) / 4 # Rough estimate
    logger.info(f"Compressed context of {len(retrieved_patents)} patents (Estimated block length: {len(compressed_block)} chars).")
    
    return {
        "compressed_block": compressed_block,
        "item_count": len(retrieved_patents)
    }
