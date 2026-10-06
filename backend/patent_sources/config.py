import os
from pydantic import BaseModel, Field

class PatentSourcesConfig(BaseModel):
    epo_enabled: bool = Field(
        default_factory=lambda: os.getenv("EPO_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    epo_base_url: str = Field(
        default_factory=lambda: os.getenv("EPO_BASE_URL", "https://data.epo.org/publication-server/rest/v1.2")
    )
    epo_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("EPO_TIMEOUT_SECONDS", "10.0"))
    )
    epo_max_retries: int = Field(
        default_factory=lambda: int(os.getenv("EPO_MAX_RETRIES", "2"))
    )
    epo_cache_enabled: bool = Field(
        default_factory=lambda: os.getenv("EPO_CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    epo_cache_dir: str = Field(
        default_factory=lambda: os.getenv("EPO_CACHE_DIR", "data/cache/epo_documents")
    )
    epo_usage_file: str = Field(
        default_factory=lambda: os.getenv("EPO_USAGE_FILE", "data/cache/epo_usage.json")
    )
    # Fair-use: 5 GB per sliding 7-day window
    epo_usage_limit_bytes: int = Field(
        default_factory=lambda: int(os.getenv("EPO_USAGE_LIMIT_BYTES", str(5 * 1024 * 1024 * 1024)))
    )
    # Safety threshold: 90% of configured budget (4.5 GB)
    epo_safety_threshold: float = Field(
        default_factory=lambda: float(os.getenv("EPO_SAFETY_THRESHOLD", "0.90"))
    )
    epo_max_results: int = Field(
        default_factory=lambda: int(os.getenv("EPO_MAX_RESULTS", "5"))
    )
    epo_max_response_bytes: int = Field(
        default_factory=lambda: int(os.getenv("EPO_MAX_RESPONSE_BYTES", str(10 * 1024 * 1024)))
    )
    source_mode: str = Field(
        default_factory=lambda: os.getenv("SOURCE_MODE", "hybrid").lower()
    )

SOURCES_CONFIG = PatentSourcesConfig()
