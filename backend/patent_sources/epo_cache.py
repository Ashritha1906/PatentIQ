import os
import json
import time
import logging
from typing import Dict, Any, Optional
from threading import Lock
from backend.patent_sources.config import SOURCES_CONFIG

logger = logging.getLogger("EPOCache")

class EPOCache:
    """
    Lightweight, thread-safe filesystem cache for EPO patent publications.
    Prevents redundant network roundtrips for previously fetched European patents.
    """

    def __init__(self, cache_dir: str = SOURCES_CONFIG.epo_cache_dir, enabled: bool = SOURCES_CONFIG.epo_cache_enabled):
        self.cache_dir = cache_dir
        self.enabled = enabled
        self.hits = 0
        self.misses = 0
        self.lock = Lock()
        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)

    def _get_path(self, identifier: str) -> str:
        # Sanitize filename: replace slashes or special characters
        clean_key = identifier.replace("/", "_").replace("\\", "_").strip()
        return os.path.join(self.cache_dir, f"{clean_key}.json")

    def get(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves cached patent record if present.
        """
        if not self.enabled:
            return None

        filepath = self._get_path(identifier)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                with self.lock:
                    self.hits += 1
                logger.debug(f"EPO Cache HIT for {identifier}")
                return entry.get("data")
            except Exception as e:
                logger.warning(f"Error reading EPO cache for {identifier}: {e}")

        with self.lock:
            self.misses += 1
        return None

    def set(self, identifier: str, data: Dict[str, Any], raw_bytes_len: int = 0):
        """
        Saves parsed patent document to the cache.
        """
        if not self.enabled:
            return

        filepath = self._get_path(identifier)
        try:
            payload = {
                "identifier": identifier,
                "fetched_at": time.time(),
                "source": "EPO_EPS",
                "byte_size": raw_bytes_len or len(json.dumps(data)),
                "data": data
            }
            temp_path = f"{filepath}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(temp_path, filepath)
            logger.debug(f"Cached EPO document: {identifier}")
        except Exception as e:
            logger.warning(f"Failed to write EPO cache for {identifier}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            cached_count = len([f for f in os.listdir(self.cache_dir) if f.endswith(".json")]) if os.path.exists(self.cache_dir) else 0
            return {
                "enabled": self.enabled,
                "hits": self.hits,
                "misses": self.misses,
                "cached_documents": cached_count
            }

EPO_CACHE = EPOCache()
