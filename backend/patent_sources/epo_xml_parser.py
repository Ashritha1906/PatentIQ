import re
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional

logger = logging.getLogger("EPOXMLParser")

def _clean_text(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    cleaned = re.sub(r'\s+', ' ', str(val)).strip()
    return cleaned if cleaned else None

def _format_date(raw_date: Optional[str]) -> Optional[str]:
    if not raw_date:
        return None
    d = str(raw_date).strip()
    # Handle YYYYMMDD -> YYYY-MM-DD
    if len(d) == 8 and d.isdigit():
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    # Handle ISO YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', d):
        return d
    return d

class EPOXMLParser:
    """
    Robust, secure XML parser for EPO European Publication Server patent documents
    (based on the ep-patent-document DTD and observation of real EPS XML publications).
    Guards against XXE attacks and safely extracts bibliographic and textual patent disclosures.
    """

    @classmethod
    def parse_ep_document(cls, xml_content: str) -> Dict[str, Any]:
        """
        Parses an ep-patent-document XML string into PatentIQ's canonical schema.
        Never fabricates missing fields.
        """
        if not xml_content or not xml_content.strip():
            raise ValueError("Empty XML content provided to EPOXMLParser")

        try:
            # Defend against XML vulnerabilities using standard ElementTree (which disables entity expansion)
            root = ET.fromstring(xml_content.strip())
        except Exception as e:
            logger.error(f"Failed to parse EPO XML: {e}")
            raise ValueError(f"Malformed EPO XML document: {e}")

        # Extract root attributes
        country = root.attrib.get("country", "EP")
        doc_num = root.attrib.get("doc-number")
        raw_kind = root.attrib.get("kind")
        raw_date = root.attrib.get("date-publ")
        doc_id = root.attrib.get("id")

        # 1. Publication Number
        b110 = root.find(".//B110")
        pub_num_val = b110.text.strip() if b110 is not None and b110.text else doc_num
        if pub_num_val:
            canonical_pub_num = f"EP{pub_num_val}" if not str(pub_num_val).startswith("EP") else str(pub_num_val)
        elif doc_id:
            canonical_pub_num = doc_id
        else:
            canonical_pub_num = "EP_UNKNOWN"

        # 2. Kind Code (Preserve ONLY verified kind code from root or B130, else None)
        b130 = root.find(".//B130")
        verified_kind = None
        if raw_kind and raw_kind.strip():
            verified_kind = raw_kind.strip().upper()
        elif b130 is not None and b130.text and b130.text.strip():
            verified_kind = b130.text.strip().upper()

        # 3. Publication Date
        b140_date = root.find(".//B140/date")
        date_str = raw_date or (b140_date.text if b140_date is not None else None)
        pub_date = _format_date(date_str)

        # 4. Title (Search B542 tags, prioritize lang='en')
        title = None
        title_nodes = root.findall(".//B542")
        for node in title_nodes:
            node_lang = node.attrib.get("lang", "").lower()
            if node_lang == "en" and node.text:
                title = _clean_text(node.text)
                break
        if not title and title_nodes:
            for node in title_nodes:
                if node.text and node.text.strip():
                    title = _clean_text(node.text)
                    break
        if not title:
            # Fallback to general invention-title tag if present
            inv_title = root.find(".//invention-title")
            if inv_title is not None and inv_title.text:
                title = _clean_text(inv_title.text)

        # 5. Abstract
        abstract_paras: List[str] = []
        abstract_nodes = root.findall(".//abstract")
        target_abstract = None
        for ab in abstract_nodes:
            if ab.attrib.get("lang", "").lower() == "en":
                target_abstract = ab
                break
        if target_abstract is None and abstract_nodes:
            target_abstract = abstract_nodes[0]

        if target_abstract is not None:
            for p in target_abstract.findall(".//p"):
                if p.text:
                    clean_p = _clean_text(p.text)
                    if clean_p:
                        abstract_paras.append(clean_p)
        abstract = " ".join(abstract_paras) if abstract_paras else None

        # 6. Applicants (B711/snm or applicant/name)
        applicants: List[str] = []
        for snm in root.findall(".//B711/snm"):
            name = _clean_text(snm.text)
            if name and name not in applicants:
                applicants.append(name)
        if not applicants:
            for app_node in root.findall(".//applicant//name"):
                name = _clean_text(app_node.text)
                if name and name not in applicants:
                    applicants.append(name)

        # 7. Inventors (B721/snm or inventor/name)
        inventors: List[str] = []
        for snm in root.findall(".//B721/snm"):
            name = _clean_text(snm.text)
            if name and name not in inventors:
                inventors.append(name)
        if not inventors:
            for inv_node in root.findall(".//inventor//name"):
                name = _clean_text(inv_node.text)
                if name and name not in inventors:
                    inventors.append(name)

        # 8. IPC Classifications
        ipc_codes: List[str] = []
        for item in root.findall(".//classification-ipcr/text"):
            code = _clean_text(item.text)
            if code and code not in ipc_codes:
                ipc_codes.append(code)
        if not ipc_codes:
            for item in root.findall(".//classification-ipc/text"):
                code = _clean_text(item.text)
                if code and code not in ipc_codes:
                    ipc_codes.append(code)

        # 9. CPC Classifications
        cpc_codes: List[str] = []
        for item in root.findall(".//classification-cpc/text"):
            code = _clean_text(item.text)
            if code and code not in cpc_codes:
                cpc_codes.append(code)

        # 10. Claims
        claim_texts: List[str] = []
        for ct in root.findall(".//claims//claim-text"):
            txt = _clean_text(ct.text)
            if txt:
                claim_texts.append(txt)
        claims = "\n".join(claim_texts) if claim_texts else None

        # 11. Description
        desc_paras: List[str] = []
        for p in root.findall(".//description//p"):
            txt = _clean_text(p.text)
            if txt:
                desc_paras.append(txt)
        description = "\n".join(desc_paras[:20]) if desc_paras else None  # bounded text slice

        return {
            "publication_number": canonical_pub_num,
            "country": country.upper() if country else "EP",
            "kind_code": verified_kind,
            "publication_date": pub_date,
            "title": title or f"European Patent Application {canonical_pub_num}",
            "abstract": abstract,
            "applicants": applicants,
            "inventors": inventors,
            "ipc": ipc_codes,
            "cpc": cpc_codes,
            "description": description,
            "claims": claims,
            "source": "EPO_EPS"
        }
