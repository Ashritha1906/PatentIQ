import os
from dotenv import load_dotenv

# Load workspace env variables
load_dotenv()

# Lens API Settings
LENS_API_KEY = os.getenv("LENS_API_KEY", "")
LENS_API_URL = "https://api.lens.org/patent/search"

# Storage Settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "vectordb")
REPORTS_DIR = os.path.join(BASE_DIR, "backend", "knowledge_expansion", "reports")
VERSION_METADATA_DIR = os.path.join(BASE_DIR, "data", "processed", "versions")

# Report file paths
SYNC_HISTORY_PATH = os.path.join(REPORTS_DIR, "sync_history.csv")
SYNC_REPORT_PATH = os.path.join(REPORTS_DIR, "knowledge_sync_report.txt")
AUDIT_REPORT_PATH = os.path.join(REPORTS_DIR, "knowledge_audit.txt")

# Performance & Rate Limits Configuration
RATE_LIMIT_RETRIES = 5
RATE_LIMIT_BACKOFF_FACTOR = 2.0
API_TIMEOUT_SECONDS = 30
DEFAULT_BATCH_SIZE = 128

# Model specifications matching the existing setup
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Ensure storage and metadata directories exist on import
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(VERSION_METADATA_DIR, exist_ok=True)
