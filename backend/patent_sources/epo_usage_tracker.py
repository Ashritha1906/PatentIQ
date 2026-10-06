import os
import json
import time
import logging
from typing import Dict, Any, List
from threading import Lock
from backend.patent_sources.config import SOURCES_CONFIG

logger = logging.getLogger("EPOUsageTracker")

class EPOUsageTracker:
    """
    Thread-safe tracker for EPO European Publication Server usage and fair-use limits.
    Monitors sliding 7-day bandwidth usage against the official 5 GB IP fair-use limit,
    enforcing a configurable 90% safety cutoff (4.5 GB) to prevent rate limiting.
    """

    def __init__(
        self,
        usage_file: str = SOURCES_CONFIG.epo_usage_file,
        limit_bytes: int = SOURCES_CONFIG.epo_usage_limit_bytes,
        safety_threshold_ratio: float = SOURCES_CONFIG.epo_safety_threshold
    ):
        self.usage_file = usage_file
        self.limit_bytes = limit_bytes
        self.safety_limit_bytes = int(limit_bytes * safety_threshold_ratio)
        self.lock = Lock()
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        dirname = os.path.dirname(self.usage_file)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load EPO usage file, initializing new state: {e}")
        return {"requests": [], "total_requests": 0, "total_all_time_bytes": 0}

    def _save_data(self, data: Dict[str, Any]):
        try:
            self._ensure_cache_dir()
            temp_file = f"{self.usage_file}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_file, self.usage_file)
        except Exception as e:
            logger.error(f"Failed to persist EPO usage data: {e}")

    def _clean_expired_requests(self, requests: List[Dict[str, Any]], now: float) -> List[Dict[str, Any]]:
        # Sliding 7-day window: 7 * 24 * 3600 seconds
        cutoff = now - (7 * 24 * 3600)
        return [r for r in requests if r.get("timestamp", 0) >= cutoff]

    def record_request(self, bytes_transferred: int, status_code: int = 200, endpoint: str = ""):
        """
        Records an outbound request to EPO EPS with byte count and response status.
        """
        with self.lock:
            now = time.time()
            data = self._load_data()
            requests = self._clean_expired_requests(data.get("requests", []), now)

            entry = {
                "timestamp": now,
                "bytes": int(bytes_transferred),
                "status_code": int(status_code),
                "endpoint": endpoint
            }
            requests.append(entry)

            data["requests"] = requests
            data["total_requests"] = data.get("total_requests", 0) + 1
            data["total_all_time_bytes"] = data.get("total_all_time_bytes", 0) + int(bytes_transferred)
            data["last_request_timestamp"] = now

            self._save_data(data)

    def get_rolling_7_day_bytes(self) -> int:
        """
        Calculates the total bytes transferred in the last 7 days.
        """
        with self.lock:
            now = time.time()
            data = self._load_data()
            requests = self._clean_expired_requests(data.get("requests", []), now)
            return sum(r.get("bytes", 0) for r in requests)

    def can_request(self) -> bool:
        """
        Returns True if current 7-day usage is below the safety threshold (4.5 GB).
        Returns False if bandwidth protection must halt live requests.
        """
        rolling_bytes = self.get_rolling_7_day_bytes()
        if rolling_bytes >= self.safety_limit_bytes:
            logger.warning(
                f"EPO safety threshold exceeded: {rolling_bytes / (1024*1024):.2f} MB "
                f">= safety limit {self.safety_limit_bytes / (1024*1024):.2f} MB. Halting live calls."
            )
            return False
        return True

    def get_usage_summary(self) -> Dict[str, Any]:
        """
        Returns structured metrics for monitoring, API responses, and debugging.
        """
        with self.lock:
            now = time.time()
            data = self._load_data()
            requests = self._clean_expired_requests(data.get("requests", []), now)
            rolling_bytes = sum(r.get("bytes", 0) for r in requests)
            percent_used = (rolling_bytes / self.limit_bytes) * 100.0 if self.limit_bytes > 0 else 0.0

            return {
                "rolling_7_day_bytes": rolling_bytes,
                "rolling_7_day_mb": round(rolling_bytes / (1024 * 1024), 2),
                "fair_use_limit_mb": round(self.limit_bytes / (1024 * 1024), 2),
                "safety_limit_mb": round(self.safety_limit_bytes / (1024 * 1024), 2),
                "percent_used": round(percent_used, 2),
                "requests_in_window": len(requests),
                "total_all_time_requests": data.get("total_requests", 0),
                "is_throttled": rolling_bytes >= self.safety_limit_bytes,
                "last_request_at": data.get("last_request_timestamp")
            }

USAGE_TRACKER = EPOUsageTracker()
