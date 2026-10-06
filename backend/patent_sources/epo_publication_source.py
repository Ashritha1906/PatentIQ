import re
import logging
from typing import List, Dict, Any, Optional
from backend.patent_sources.base import PatentSource
from backend.patent_sources.config import SOURCES_CONFIG
from backend.patent_sources.epo_client import EPO_CLIENT
from backend.patent_sources.epo_xml_parser import EPOXMLParser
from backend.patent_sources.epo_cache import EPO_CACHE
from backend.patent_sources.epo_usage_tracker import USAGE_TRACKER
from backend.retrieval.query_model import PatentSearchResult

logger = logging.getLogger("EPOPublicationSource")

class EPOPublicationSource(PatentSource):
    """
    Live European Patent Office (EPO) European Publication Server (EPS) provider.
    Enriches PatentIQ with official European A and B publications on demand.
    Complies with free fair-use limits (5 GB/7 days), supports XML parsing,
    document caching, and fails gracefully to local retrieval if unavailable.
    """

    @property
    def name(self) -> str:
        return "EPO_EPS"

    def _dict_to_search_result(self, doc: Dict[str, Any], score: float = 0.5, reasons: Optional[List[str]] = None) -> PatentSearchResult:
        pub_num = doc.get("publication_number", "EP_UNKNOWN")
        apps = doc.get("applicants", [])
        applicant_str = ", ".join(apps[:2]) if apps else None
        
        ipc_list = doc.get("ipc", [])
        ipc_str = ipc_list[0] if ipc_list else None

        return PatentSearchResult(
            patent_id=f"epo_{pub_num}",
            publication_number=pub_num,
            title=doc.get("title") or f"European Patent Application {pub_num}",
            abstract=doc.get("abstract"),
            applicant=applicant_str,
            inventors=doc.get("inventors") or [],
            publication_date=doc.get("publication_date"),
            country="EP",
            document_number=pub_num.replace("EP", ""),
            kind_code=doc.get("kind_code"),  # Preserved strictly, None if not provided
            classification=ipc_str,
            semantic_score=score,
            keyword_score=score,
            final_score=score,
            ranking_reasons=reasons or ["Retrieved live from EPO European Publication Server"],
            source=self.name,
            source_url=f"https://data.epo.org/publication-server/rest/v1.2/patents/{pub_num}"
        )

    def fetch_document(self, identifier: str) -> Optional[PatentSearchResult]:
        """
        Fetches an EPO patent document by identifier, using local cache first, then live EPS.
        """
        clean_id = identifier.strip().upper()
        if not clean_id.startswith("EP") and re.match(r'^\d{7}', clean_id):
            clean_id = f"EP{clean_id}"

        # 1. Check local cache
        cached = EPO_CACHE.get(clean_id)
        if cached:
            return self._dict_to_search_result(cached, score=1.0, reasons=["Retrieved from local EPO cache"])

        # 2. Check fair-use limit
        if not USAGE_TRACKER.can_request():
            logger.warning(f"EPO bandwidth safety limit reached. Cannot fetch {clean_id}.")
            return None

        # 3. Live XML fetch
        try:
            xml_str = EPO_CLIENT.fetch_patent_xml(clean_id)
            if not xml_str:
                logger.info(f"EPO document {clean_id} not found on European Publication Server.")
                return None

            parsed = EPOXMLParser.parse_ep_document(xml_str)
            EPO_CACHE.set(clean_id, parsed, raw_bytes_len=len(xml_str))
            return self._dict_to_search_result(parsed, score=1.0, reasons=["Retrieved live from EPO EPS REST API"])
        except Exception as e:
            logger.error(f"Error fetching EPO document {clean_id}: {e}", exc_info=True)
            return None

    def search(
        self,
        query: str,
        concepts: Optional[List[str]] = None,
        top_k: int = SOURCES_CONFIG.epo_max_results,
        **kwargs
    ) -> List[PatentSearchResult]:
        """
        On-demand live search and enrichment from EPO European Publication Server.
        Extracts relevant European publications matching technical concepts.
        Fails gracefully (returning []) if EPO is unreachable, throttled, or errors.
        """
        if not SOURCES_CONFIG.epo_enabled:
            logger.debug("EPO live source is disabled by configuration.")
            return []

        if not USAGE_TRACKER.can_request():
            logger.warning("EPO fair-use threshold reached. Live retrieval bypassed.")
            return []

        results: List[PatentSearchResult] = []

        try:
            # 1. Check if the query specifically mentions an EP publication identifier
            ep_matches = re.findall(r'\b(EP\s?\d{7}[A-Z0-9]*)\b', query, re.IGNORECASE)
            if ep_matches:
                for ep_id in ep_matches[:top_k]:
                    clean = ep_id.replace(" ", "").upper()
                    doc = self.fetch_document(clean)
                    if doc:
                        doc.final_score = 0.95
                        doc.ranking_reasons = ["Exact EP publication match via EPO EPS"]
                        results.append(doc)
                if results:
                    return results

            # 2. Concept-based discovery from recent weekly publication batches
            search_terms = []
            if concepts:
                search_terms.extend([c.lower().strip() for c in concepts if len(c.strip()) > 3])
            # Add significant query keywords
            words = [w.lower() for w in re.findall(r'[a-zA-Z]{4,}', query) if w.lower() not in ("patent", "patents", "find", "system", "method", "using", "related")]
            search_terms.extend(words[:4])
            search_terms = list(dict.fromkeys(search_terms))

            if not search_terms:
                return []

            dates = EPO_CLIENT.get_publication_dates()
            if not dates:
                return []

            # Check latest publication batch (on-demand sampling)
            candidate_ids = EPO_CLIENT.get_patents_for_date(dates[0])
            if not candidate_ids:
                return []

            # Sample bounded set of candidates to protect fair-use limit
            scored_candidates = []
            for cand_id in candidate_ids[:15]:
                # Prefer cached or fetch bounded
                doc_obj = self.fetch_document(cand_id)
                if not doc_obj:
                    continue

                text_to_match = f"{doc_obj.title} {doc_obj.abstract or ''}".lower()
                matches = [term for term in search_terms if term in text_to_match]
                if matches:
                    rel_score = float(len(matches)) / float(max(len(search_terms), 1))
                    rel_score = round(min(1.0, 0.4 + (0.5 * rel_score)), 4)
                    doc_obj.semantic_score = rel_score
                    doc_obj.keyword_score = rel_score
                    doc_obj.final_score = rel_score
                    doc_obj.ranking_reasons = [f"Live EPO match: terms matched ({', '.join(matches[:3])})"]
                    scored_candidates.append(doc_obj)

                if len(scored_candidates) >= top_k:
                    break

            scored_candidates.sort(key=lambda x: x.final_score, reverse=True)
            return scored_candidates[:top_k]

        except Exception as e:
            # Crucial: Never crash entire pipeline on EPO failure
            logger.warning(f"EPO live search encountered non-fatal error: {e}. Falling back gracefully.")
            return []

    def health_check(self) -> Dict[str, Any]:
        return EPO_CLIENT.check_health()

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "source": self.name,
            "type": "Live REST API (v1.2)",
            "jurisdiction": "European Patent Office (EP)",
            "update_cadence": "Weekly",
            "formats": ["XML", "HTML", "PDF"],
            "fair_use_limit": "5 GB per sliding 7-day window",
            "safety_cutoff": "4.5 GB (90%)",
            "usage_status": USAGE_TRACKER.get_usage_summary()
        }
