import os
import csv
import logging
from datetime import datetime
from typing import Dict, Any
from backend.knowledge_expansion.config import (
    SYNC_HISTORY_PATH,
    SYNC_REPORT_PATH,
    AUDIT_REPORT_PATH
)

logger = logging.getLogger("AuditLogger")

class AuditLogger:
    """
    Manages auditing and version reports for database synchronizations.
    Updates sync_history.csv and generates text summaries of ingestion updates.
    """
    def __init__(self):
        self.history_path = SYNC_HISTORY_PATH
        self.report_path = SYNC_REPORT_PATH
        self.audit_path = AUDIT_REPORT_PATH

    def log_sync(self, stats: Dict[str, Any]) -> None:
        """
        Appends a run metadata record to the CSV historical sync database
        and compiles a detailed report file.
        """
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        
        # 1. Write to CSV
        file_exists = os.path.exists(self.history_path)
        headers = [
            "version_id", "timestamp", "source", "added_count", 
            "skipped_count", "failed_count", "embedding_duration", 
            "vector_duration", "total_duration", "peak_ram_mb", "storage_size_mb"
        ]
        
        try:
            with open(self.history_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                if not file_exists:
                    writer.writeheader()
                    
                writer.writerow({
                    "version_id": stats.get("version_id", "v1"),
                    "timestamp": stats.get("timestamp", datetime.now().isoformat()),
                    "source": stats.get("source", "Lens Sync"),
                    "added_count": stats.get("added_count", 0),
                    "skipped_count": stats.get("skipped_count", 0),
                    "failed_count": stats.get("failed_count", 0),
                    "embedding_duration": f"{stats.get('embedding_duration', 0.0):.2f}",
                    "vector_duration": f"{stats.get('vector_duration', 0.0):.2f}",
                    "total_duration": f"{stats.get('total_duration', 0.0):.2f}",
                    "peak_ram_mb": f"{stats.get('peak_ram_mb', 0.0):.2f}",
                    "storage_size_mb": f"{stats.get('storage_size_mb', 0.0):.2f}"
                })
        except Exception as e:
            logger.error(f"Failed to append sync history: {e}")

        # 2. Write txt sync report
        try:
            with open(self.report_path, "w", encoding="utf-8") as f:
                f.write("==================================================\n")
                f.write("PATENTIQ - KNOWLEDGE BASE SYNCHRONIZATION REPORT\n")
                f.write("==================================================\n")
                f.write(f"Sync Timestamp      : {stats.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}\n")
                f.write(f"Knowledge Version   : {stats.get('version_id', 'v1')}\n")
                f.write(f"Trigger Source      : {stats.get('source', 'Manual')}\n")
                f.write("--------------------------------------------------\n")
                f.write(f"Patents Processed   : {stats.get('total_processed', 0)}\n")
                f.write(f"Patents Ingested    : {stats.get('added_count', 0)}\n")
                f.write(f"Duplicates Skipped  : {stats.get('skipped_count', 0)}\n")
                f.write(f"Failures / Errors   : {stats.get('failed_count', 0)}\n")
                f.write("--------------------------------------------------\n")
                f.write(f"Embedding Duration  : {stats.get('embedding_duration', 0.0):.2f} seconds\n")
                f.write(f"Vector DB Duration  : {stats.get('vector_duration', 0.0):.2f} seconds\n")
                f.write(f"Total Sync Duration : {stats.get('total_duration', 0.0):.2f} seconds\n")
                f.write("--------------------------------------------------\n")
                f.write(f"Peak RAM Usage      : {stats.get('peak_ram_mb', 0.0):.2f} MB\n")
                f.write(f"Vector Store Size   : {stats.get('storage_size_mb', 0.0):.2f} MB\n")
                f.write(f"Integrity Status    : {'SUCCESS' if stats.get('integrity_verified', True) else 'FAILED'}\n")
                f.write("==================================================\n")
        except Exception as e:
            logger.error(f"Failed to generate txt report: {e}")

    def log_audit(self, audit_results: Dict[str, Any]) -> None:
        """Generates a detailed integrity check audit report."""
        try:
            with open(self.audit_path, "w", encoding="utf-8") as f:
                f.write("==================================================\n")
                f.write("PATENTIQ - KNOWLEDGE DB AUDIT & INTEGRITY CHECK\n")
                f.write("==================================================\n")
                f.write(f"Audit Timestamp     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Database Collection : patentiq_patents\n")
                f.write("--------------------------------------------------\n")
                f.write(f"Total Vector Count  : {audit_results.get('total_vectors', 0)}\n")
                f.write(f"Metadata Records    : {audit_results.get('metadata_count', 0)}\n")
                f.write(f"Dimension Check     : {'384 (all-MiniLM-L6-v2) - OK' if audit_results.get('dimensions_valid', True) else 'INVALID'}\n")
                f.write(f"Empty Document IDs  : {audit_results.get('empty_ids_count', 0)}\n")
                f.write(f"Duplicate IDs Found : {audit_results.get('duplicate_ids_count', 0)}\n")
                f.write(f"Null Values Found   : {audit_results.get('null_fields_count', 0)}\n")
                f.write("--------------------------------------------------\n")
                f.write(f"System Health Status: {audit_results.get('health_status', 'HEALTHY')}\n")
                f.write(f"Audit Recommendation: {audit_results.get('recommendation', 'No action needed.')}\n")
                f.write("==================================================\n")
        except Exception as e:
            logger.error(f"Failed to write audit logs: {e}")
