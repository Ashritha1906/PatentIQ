import re
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("Normalizer")

# Compile corporate suffixes regex for standardization
CORP_SUFFIX_RX = re.compile(
    r'\b(LTD|L\.T\.D\.|LLC|L\.L\.C\.|INC|I\.N\.C\.|CORP|CORPORATION|CO|COMPANY|S\.A\.|AG|GMBH|S\.P\.A\.|PLC|INCORPORATED|TECHNOLOGIES|TECHNOLOGY|SYSTEMS|SOLUTIONS|HOLDINGS|IP|GROUP|GLOBAL|USA|ASIA|EUROPE|DEV|DEVELOPMENT|RESEARCH)\b', 
    re.IGNORECASE
)

def clean_whitespace(text: str) -> str:
    """Removes non-printable characters and normalizes consecutive whitespaces to a single space."""
    if not text:
        return ""
    cleaned = "".join(ch for ch in text if ch.isprintable())
    cleaned = cleaned.replace('\ufffd', '')
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def normalize_applicant(name: str) -> str:
    """
    Standardizes applicant names by converting to uppercase, stripping special punctuation,
    and removing trailing corporate suffixes (e.g. SAMSUNG CO LTD -> SAMSUNG).
    """
    if not name or name.lower() == "unknown":
        return "Unknown"
    
    # Process multiple separated names
    names = [n.strip() for n in name.split(";")]
    normalized_names = []
    
    for n in names:
        # Convert to upper
        u_name = n.upper()
        # Strip corporate suffixes
        cleaned = CORP_SUFFIX_RX.sub("", u_name)
        # Strip special punctuation but preserve internal spaces
        cleaned = re.sub(r'[^\w\s-]', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        if cleaned:
            normalized_names.append(cleaned)
            
    # Deduplicate normalized names
    seen = set()
    deduped = []
    for nn in normalized_names:
        if nn not in seen:
            seen.add(nn)
            deduped.append(nn)
            
    return "; ".join(deduped) if deduped else "Unknown"

def normalize_ipc(ipc: str) -> str:
    """Cleans and normalizes IPC lists to uppercase, comma-separated format."""
    if not ipc or ipc.lower() == "unknown":
        return "Unknown"
    
    parts = [p.strip().upper() for p in ipc.split(",")]
    # Clean and validate format
    valid_parts = [p for p in parts if p]
    return ", ".join(valid_parts) if valid_parts else "Unknown"

def normalize_date(date_str: str) -> str:
    """Parses date string and outputs standardized YYYY-MM-DD. Fallback to 'Unknown'."""
    if not date_str or date_str.lower() in ("unknown", "nan", "none"):
        return "Unknown"
    
    # Try different date formats
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y%m%d"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
            
    # Try checking for YYYY prefix
    match = re.match(r'\b(19|20)\d{2}\b', date_str)
    if match:
        return f"{match.group(0)}-01-01"
        
    return "Unknown"

def build_patent_text(patent: Dict[str, Any]) -> str:
    """
    Constructs the canonical text representation used for creating embeddings.
    Adheres exactly to the Title, Field, IPC, and Applicant template defined in Phase 2.
    """
    title = clean_whitespace(patent.get("title", ""))
    field = clean_whitespace(patent.get("field_of_invention", ""))
    ipc = clean_whitespace(patent.get("classification_ipc", ""))
    applicant = clean_whitespace(patent.get("applicant_name", ""))
    
    # Defaults
    title = title if title else "Unknown Title"
    field = field if field else "Unknown Field"
    ipc = ipc if ipc else "Unknown IPC"
    applicant = applicant if applicant else "Unknown Applicant"
    
    return (
        f"Title: {title}\n\n"
        f"Field Of Invention: {field}\n\n"
        f"IPC Classification: {ipc}\n\n"
        f"Applicant: {applicant}"
    )

def normalize_patent(patent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans and standardizes all metadata keys inside a parsed patent dictionary.
    Builds the final 'patent_text' text representation field.
    """
    normalized = patent.copy()
    
    normalized["title"] = clean_whitespace(patent.get("title", "Unknown Title"))
    normalized["applicant_name"] = normalize_applicant(patent.get("applicant_name", "Unknown"))
    normalized["classification_ipc"] = normalize_ipc(patent.get("classification_ipc", "Unknown"))
    normalized["publication_date"] = normalize_date(patent.get("publication_date", "Unknown"))
    
    # Build text representation used for vectorization
    normalized["patent_text"] = build_patent_text(normalized)
    
    return normalized
