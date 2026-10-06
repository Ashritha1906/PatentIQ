import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from backend.knowledge_expansion.config import VERSION_METADATA_DIR

logger = logging.getLogger("Scheduler")

class SyncScheduler:
    """
    Manages synchronization schedules and calculates scheduled execute intervals.
    Supports Manual, Daily, Weekly, and Monthly triggers.
    """
    def __init__(self):
        self.config_path = os.path.join(VERSION_METADATA_DIR, "scheduler_config.json")

    def get_config(self) -> Dict[str, Any]:
        """Loads and returns the active scheduler configuration from disk."""
        if not os.path.exists(self.config_path):
            config = {
                "mode": "manual",
                "interval_hours": 24,
                "next_sync": None,
                "enabled": False
            }
            self.save_config(config)
            return config
            
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read scheduler config: {e}")
            return {"mode": "manual", "next_sync": None, "enabled": False}

    def save_config(self, config: Dict[str, Any]) -> None:
        """Saves scheduler configuration to disk."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save scheduler config: {e}")

    def set_schedule(self, mode: str) -> Dict[str, Any]:
        """Sets the active sync schedule mode and calculates the next execution timestamp."""
        mode_lower = mode.lower().strip()
        now = datetime.now()
        next_sync = None
        enabled = True

        if mode_lower == "daily":
            next_sync = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif mode_lower == "weekly":
            # Schedule next Sunday midnight
            days_ahead = 6 - now.weekday()
            if days_ahead <= 0: days_ahead += 7
            next_sync = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif mode_lower == "monthly":
            # Schedule 1st of next month midnight
            if now.month == 12:
                next_sync = datetime(now.year + 1, 1, 1)
            else:
                next_sync = datetime(now.year, now.month + 1, 1)
        else:
            mode_lower = "manual"
            enabled = False

        config = {
            "mode": mode_lower,
            "next_sync": next_sync.isoformat() if next_sync else None,
            "enabled": enabled,
            "updated_at": now.isoformat()
        }
        
        self.save_config(config)
        logger.info(f"Sync schedule set to {mode_lower.upper()}. Next execution: {config['next_sync']}")
        return config
