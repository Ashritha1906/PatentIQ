import re
import time
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from backend.patent_sources.config import SOURCES_CONFIG
from backend.patent_sources.epo_usage_tracker import USAGE_TRACKER

logger = logging.getLogger("EPOClient")

class EPOClient:
    """
    Dedicated HTTP client for the official European Patent Office (EPO)
    European Publication Server (EPS) REST API v1.2.
    Provides connection handling, bounded retries with backoff, fair-use bandwidth
    tracking, response size monitoring, and graceful failure fallbacks.
    """

    def __init__(
        self,
        base_url: str = SOURCES_CONFIG.epo_base_url,
        timeout: float = SOURCES_CONFIG.epo_timeout_seconds,
        max_retries: int = SOURCES_CONFIG.epo_max_retries,
        max_response_bytes: int = SOURCES_CONFIG.epo_max_response_bytes
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_response_bytes = max_response_bytes

    def _make_request(self, endpoint: str) -> Optional[str]:
        """
        Executes an HTTP GET request to EPO EPS with retry, backoff, and usage tracking.
        """
        if not USAGE_TRACKER.can_request():
            logger.warning("EPO usage budget reached. Skipping live HTTP request.")
            return None

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "User-Agent": "PatentIQ-KnowledgeExpansion/1.0",
            "Accept": "application/xml, text/html, */*"
        }

        for attempt in range(self.max_retries + 1):
            start_time = time.time()
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    status_code = resp.status
                    data = resp.read(self.max_response_bytes)
                    latency_ms = (time.time() - start_time) * 1000

                    bytes_len = len(data)
                    USAGE_TRACKER.record_request(bytes_len, status_code=status_code, endpoint=endpoint)

                    logger.debug(f"EPO GET {endpoint} succeeded ({status_code}, {bytes_len} bytes, {latency_ms:.1f}ms)")
                    return data.decode("utf-8", errors="replace")

            except urllib.error.HTTPError as e:
                latency_ms = (time.time() - start_time) * 1000
                USAGE_TRACKER.record_request(0, status_code=e.code, endpoint=endpoint)
                logger.warning(f"EPO HTTP {e.code} for {endpoint} (attempt {attempt+1}/{self.max_retries+1})")
                if e.code in (404, 400):
                    return None  # Non-retryable
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                logger.warning(f"EPO connection error for {endpoint}: {e} (attempt {attempt+1}/{self.max_retries+1})")

            # Exponential backoff before retry (1.0s, 2.0s)
            if attempt < self.max_retries:
                time.sleep(1.0 * (2 ** attempt))

        return None

    def get_publication_dates(self) -> List[str]:
        """
        Retrieves the latest available weekly publication batch dates from EPS (e.g. ['20260930', ...]).
        """
        html = self._make_request("publication-dates")
        if not html:
            return []
        dates = re.findall(r'/publication-dates/(\d{8})/patents', html)
        return list(dict.fromkeys(dates))

    def get_patents_for_date(self, date_str: str) -> List[str]:
        """
        Lists patent publication identifiers released on the specified date.
        """
        html = self._make_request(f"publication-dates/{date_str}/patents")
        if not html:
            return []
        patents = re.findall(r'/patents/([A-Z0-9]+)', html)
        return list(dict.fromkeys(patents))

    def fetch_patent_xml(self, patent_id: str) -> Optional[str]:
        """
        Fetches the primary document.xml representation for a given EP patent identifier.
        """
        clean_id = patent_id.strip()
        # Direct document.xml path
        xml_content = self._make_request(f"patents/{clean_id}/document.xml")
        if xml_content:
            return xml_content

        # Fallback: if patent_id doesn't include correction code (e.g. EP4812013A1 -> EP4812013NWA1)
        if not re.search(r'[A-Z]{2}[A-Z]\d?$', clean_id):
            alt_id = re.sub(r'([A-Z]\d?)$', r'NW\1', clean_id)
            if alt_id != clean_id:
                return self._make_request(f"patents/{alt_id}/document.xml")

        return None

    def check_health(self) -> Dict[str, Any]:
        """
        Quick connectivity and availability check against the EPS base URL.
        """
        if not USAGE_TRACKER.can_request():
            return {
                "status": "throttled",
                "message": "Fair-use bandwidth safety threshold reached",
                "usage": USAGE_TRACKER.get_usage_summary()
            }
        try:
            dates = self.get_publication_dates()
            return {
                "status": "healthy" if dates else "degraded",
                "latest_batch": dates[0] if dates else None,
                "usage": USAGE_TRACKER.get_usage_summary()
            }
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e),
                "usage": USAGE_TRACKER.get_usage_summary()
            }

EPO_CLIENT = EPOClient()
