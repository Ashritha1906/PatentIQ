import httpx
import time
import logging
from typing import Dict, Any, Optional
from backend.knowledge_expansion.config import (
    LENS_API_URL,
    RATE_LIMIT_RETRIES,
    RATE_LIMIT_BACKOFF_FACTOR,
    API_TIMEOUT_SECONDS
)
from backend.knowledge_expansion.authentication import get_auth_headers

logger = logging.getLogger("LensClient")

class LensClientError(Exception):
    """Base exception for all Lens client query operations."""
    pass

class LensRateLimitError(LensClientError):
    """Exception raised when API requests exceed throttling limits (HTTP 429)."""
    pass

class LensPatentClient:
    """
    Reusable HTTP search client interfacing with the Lens.org Patent Search API.
    Supports retries, backoffs, and queries for dates, keywords, and classifications.
    """
    def __init__(self):
        self.url = LENS_API_URL

    def _execute_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a POST request to Lens with authentication headers.
        Implements exponential backoff on HTTP 429 (rate limits).
        """
        headers = get_auth_headers()
        backoff = 1.0
        
        for attempt in range(RATE_LIMIT_RETRIES + 1):
            try:
                logger.info(f"Executing Lens API query (Attempt {attempt + 1}/{RATE_LIMIT_RETRIES + 1})...")
                
                with httpx.Client(timeout=API_TIMEOUT_SECONDS) as client:
                    resp = client.post(self.url, headers=headers, json=payload)
                    
                    if resp.status_code == 200:
                        return resp.json()
                        
                    elif resp.status_code == 429:
                        if attempt == RATE_LIMIT_RETRIES:
                            raise LensRateLimitError("Rate limit exceeded and retries exhausted.")
                        
                        sleep_time = backoff * RATE_LIMIT_BACKOFF_FACTOR
                        logger.warning(f"Throttled (HTTP 429). Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                        backoff = sleep_time
                        
                    else:
                        logger.error(f"Lens API returned status {resp.status_code}: {resp.text}")
                        raise LensClientError(f"API query failed with status {resp.status_code}: {resp.text}")
                        
            except httpx.RequestError as e:
                if attempt == RATE_LIMIT_RETRIES:
                    raise LensClientError(f"HTTP request failed: {e}")
                
                sleep_time = backoff * RATE_LIMIT_BACKOFF_FACTOR
                logger.warning(f"Network error: {e}. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                backoff = sleep_time

        raise LensClientError("Failed to execute query after max retries.")

    def search(self, query_dsl: Dict[str, Any], size: int = 10, from_idx: int = 0, scroll: Optional[str] = None, scroll_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generic search endpoint returning raw Lens documents matching an Elasticsearch Query DSL payload.
        """
        payload: Dict[str, Any] = {
            "size": size
        }
        
        if scroll_id:
            payload["scroll_id"] = scroll_id
        else:
            payload["query"] = query_dsl
            payload["from"] = from_idx
            if scroll:
                payload["scroll"] = scroll

        return self._execute_request(payload)

    def search_by_keyword(self, keyword: str, size: int = 10, from_idx: int = 0) -> Dict[str, Any]:
        """
        Searches patents containing a keyword in title, abstract, or claims.
        """
        query_dsl = {
            "query_string": {
                "query": keyword
            }
        }
        return self.search(query_dsl, size=size, from_idx=from_idx)

    def search_by_date_range(self, start_date: str, end_date: str, size: int = 10, from_idx: int = 0) -> Dict[str, Any]:
        """
        Searches patents published within a given date range (YYYY-MM-DD format).
        """
        query_dsl = {
            "range": {
                "date_published": {
                    "gte": start_date,
                    "lte": end_date
                }
            }
        }
        return self.search(query_dsl, size=size, from_idx=from_idx)

    def search_by_applicant(self, applicant: str, size: int = 10, from_idx: int = 0) -> Dict[str, Any]:
        """
        Searches patents filed by a specific applicant.
        """
        query_dsl = {
            "match": {
                "biblio.applicants.extracted_name.value": applicant
            }
        }
        return self.search(query_dsl, size=size, from_idx=from_idx)

    def search_by_technology_class(self, ipc_symbol: str, size: int = 10, from_idx: int = 0) -> Dict[str, Any]:
        """
        Searches patents matching an IPC classification symbol.
        """
        query_dsl = {
            "match": {
                "biblio.classifications_ipc.symbol": ipc_symbol
            }
        }
        return self.search(query_dsl, size=size, from_idx=from_idx)
