import re
from typing import Dict, Any, Optional

def normalize_patent_identifier(raw_id: str) -> Dict[str, Any]:
    """
    Normalizes patent identifiers into canonical components:
      - publication_number: Canonical identifier string (preserved unchanged from source)
      - country: Two-letter ISO country code when supported by the identifier, else None
      - document_number: Canonical document number
      - kind_code: Publication kind code ONLY when explicitly provided by source/identifier, else None
      - publication_year: Inferred publication / filing year where present
    """
    if not raw_id:
        return {
            "publication_number": "UNKNOWN",
            "country": None,
            "document_number": "UNKNOWN",
            "kind_code": None,
            "publication_year": None
        }

    clean_id = str(raw_id).strip()

    # Format 1: Modern 12-digit IPO standard (e.g. 201941048032, 201811024989)
    if re.match(r'^\d{12}$', clean_id):
        return {
            "publication_number": clean_id,
            "country": "IN",
            "document_number": clean_id,
            "kind_code": None,
            "publication_year": int(clean_id[:4])
        }

    # Format 2: Regional IPO office slash format (e.g. 1/CHE/2010, 9990/DELNP/2011)
    slash_match = re.match(r'^(\d+)/([A-Z]+)/(\d{4})$', clean_id, re.IGNORECASE)
    if slash_match:
        serial, office, yr = slash_match.groups()
        canonical_str = f"{serial}/{office.upper()}/{yr}"
        return {
            "publication_number": clean_id,
            "country": "IN",
            "document_number": canonical_str,
            "kind_code": None,
            "publication_year": int(yr)
        }

    # Format 3: International standard (e.g. US10123456B2, EP3124567A1, WO2021012345)
    intl_match = re.match(r'^([A-Z]{2})(\d+)([A-Z]\d?)?$', clean_id, re.IGNORECASE)
    if intl_match:
        country, doc_num, kind = intl_match.groups()
        kind_str = kind.upper() if kind else None
        return {
            "publication_number": clean_id,
            "country": country.upper(),
            "document_number": doc_num,
            "kind_code": kind_str,
            "publication_year": None
        }

    # Fallback: preserve string faithfully as canonical publication_number
    yr_match = re.search(r'\b(19\d{2}|20\d{2})\b', clean_id)
    return {
        "publication_number": clean_id,
        "country": None,
        "document_number": clean_id,
        "kind_code": None,
        "publication_year": int(yr_match.group(1)) if yr_match else None
    }

def normalize_patent_record(patent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriches and standardizes a patent result dictionary with canonical identifier fields.
    Preserves verified kind_code, country, and publication_date only when supported by source data.
    Never infers kind_code = 'A' or invents missing dates.
    """
    raw_id = (
        patent.get("publication_number") or
        patent.get("application_number") or
        patent.get("patent_id") or
        ""
    )
    id_info = normalize_patent_identifier(str(raw_id))

    # Standardize primary fields without mutating original content
    normalized = dict(patent)
    normalized["publication_number"] = str(raw_id).strip() if raw_id else id_info["publication_number"]
    normalized["country"] = patent.get("country") or id_info.get("country")
    normalized["document_number"] = patent.get("document_number") or id_info.get("document_number")
    
    # 1. Preserve existing verified kind_code; return None if source does not provide one
    normalized["kind_code"] = patent.get("kind_code") or id_info.get("kind_code")

    # 2. Preserve publication_date only when supported by source data (never invent arbitrary dates)
    normalized["publication_date"] = patent.get("publication_date") or None

    # Ensure application_number matches publication_number for legacy consumers
    if "application_number" not in normalized or not normalized["application_number"]:
        normalized["application_number"] = normalized["publication_number"]

    return normalized
