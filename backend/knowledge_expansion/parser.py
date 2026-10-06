import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("PatentParser")

def map_ipc_to_domain(ipc_symbols: List[str]) -> str:
    """
    Infers the technology domain classification from the IPC symbols.
    Aligns with existing categories used by the retrieval and orchestrator modules.
    """
    if not ipc_symbols:
        return "COMPUTER SCIENCE"
        
    for symbol in ipc_symbols:
        sym = symbol.upper().strip()
        if sym.startswith(("G06", "G16", "G09", "G11")):
            return "COMPUTER SCIENCE"
        elif sym.startswith(("H04W", "H04L", "H04B", "H04Q", "H04J")):
            return "COMMUNICATION"
        elif sym.startswith(("H01M", "H02J", "H02M", "H02N", "H02P", "H01F")):
            return "ELECTRICAL"
        elif sym.startswith(("H01", "H03", "H05", "G01R", "G02F")):
            return "ELECTRONICS"
        elif sym.startswith(("A61B", "A61F", "A61N", "A61H", "A61M")):
            return "BIO-MEDICAL ENGINEERING"
        elif sym.startswith(("C12N", "C12Q", "C12P", "C07K", "A61K")):
            return "BIOTECHNOLOGY"
        elif sym.startswith(("F03D", "F03B", "B60", "F16", "F01", "F02", "B64")):
            return "MECHANICAL ENGINEERING"

    return "COMPUTER SCIENCE"

def parse_lens_patent(lens_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses a raw patent response dictionary from Lens API into the PatentIQ schema.
    Returns standard database fields and optional attributes.
    """
    biblio = lens_record.get("biblio", {})
    
    # 1. Resolve Application Number (Primary Identifier)
    app = biblio.get("application", {})
    app_num = app.get("number")
    if not app_num:
        app_num = lens_record.get("doc_key")
    if not app_num:
        app_num = lens_record.get("lens_id")
    if not app_num:
        app_num = "UNKNOWN_APP_" + str(hash(str(lens_record)))
    
    app_num = str(app_num).strip()
    
    # 2. Title
    title_list = biblio.get("title", [])
    title = "Unknown Title"
    if title_list:
        if isinstance(title_list, list) and len(title_list) > 0:
            title = title_list[0].get("text", "Unknown Title") if isinstance(title_list[0], dict) else str(title_list[0])
        elif isinstance(title_list, str):
            title = title_list

    # 3. Abstract
    abstract_list = lens_record.get("abstract", [])
    abstract = ""
    if abstract_list:
        if isinstance(abstract_list, list) and len(abstract_list) > 0:
            abstract = abstract_list[0].get("text", "") if isinstance(abstract_list[0], dict) else str(abstract_list[0])
        elif isinstance(abstract_list, str):
            abstract = abstract_list

    # 4. Claims
    claims_list = lens_record.get("claims", [])
    claims = ""
    if claims_list:
        if isinstance(claims_list, list) and len(claims_list) > 0:
            claims = "\n".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in claims_list])
        elif isinstance(claims_list, str):
            claims = claims_list

    # 5. Publication Date
    pub_date = biblio.get("publication_date", "Unknown")

    # 6. Applicants (Assignees)
    applicants = []
    for applicant_entry in biblio.get("applicants", []):
        name_val = applicant_entry.get("extracted_name", {}).get("value")
        if not name_val:
            name_val = applicant_entry.get("name")
        if name_val:
            applicants.append(str(name_val).strip())
    applicant_name = "; ".join(applicants) if applicants else "Unknown"

    # 7. Inventors
    inventors = []
    for inventor_entry in biblio.get("inventors", []):
        name_val = inventor_entry.get("extracted_name", {}).get("value")
        if not name_val:
            name_val = inventor_entry.get("name")
        if name_val:
            inventors.append(str(name_val).strip())

    # 8. IPC Classifications
    ipc_symbols = []
    ipc_data = biblio.get("classifications_ipc", {})
    if isinstance(ipc_data, dict):
        for classification in ipc_data.get("classifications", []):
            symbol = classification.get("symbol")
            if symbol:
                ipc_symbols.append(str(symbol).strip())
    classification_ipc = ", ".join(ipc_symbols) if ipc_symbols else "Unknown"

    # 9. CPC Classifications
    cpc_symbols = []
    cpc_data = biblio.get("classifications_cpc", {})
    if isinstance(cpc_data, dict):
        for classification in cpc_data.get("classifications", []):
            symbol = classification.get("symbol")
            if symbol:
                cpc_symbols.append(str(symbol).strip())

    # 10. Technology Domain Mapping
    field_of_invention = map_ipc_to_domain(ipc_symbols)

    # 11. Families, Citations, Legal Status (Optional properties)
    simple_family = []
    family_data = lens_record.get("families", {}).get("simple_family", {})
    if isinstance(family_data, dict):
        simple_family = [m.get("lens_id") for m in family_data.get("members", []) if m.get("lens_id")]

    legal_status_granted = lens_record.get("legal_status", {}).get("granted", False)
    jurisdiction = lens_record.get("jurisdiction", "US")

    return {
        "application_number": app_num,
        "publication_number": biblio.get("publication_number", "Unknown"),
        "title": title,
        "abstract": abstract,
        "claims": claims,
        "description": lens_record.get("description", ""),
        "publication_date": pub_date,
        "applicant_name": applicant_name,
        "inventors": inventors,
        "classification_ipc": classification_ipc,
        "classification_cpc": cpc_symbols,
        "field_of_invention": field_of_invention,
        "jurisdiction": jurisdiction,
        "patent_family": simple_family,
        "legal_status_granted": legal_status_granted,
        "forward_citations_count": len(lens_record.get("citations", {}).get("forward", [])),
        "backward_citations_count": len(lens_record.get("citations", {}).get("backward", []))
    }
