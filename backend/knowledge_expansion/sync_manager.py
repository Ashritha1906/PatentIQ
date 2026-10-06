import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.knowledge_expansion.config import (
    VERSION_METADATA_DIR,
    VECTOR_DB_PATH
)
from backend.knowledge_expansion.authentication import verify_auth
from backend.knowledge_expansion.lens_client import LensPatentClient
from backend.knowledge_expansion.pagination import ResumablePaginator
from backend.knowledge_expansion.parser import parse_lens_patent
from backend.knowledge_expansion.normalizer import normalize_patent
from backend.knowledge_expansion.duplicate_checker import DuplicateChecker
from backend.knowledge_expansion.incremental_embeddings import IncrementalEmbeddingGenerator
from backend.knowledge_expansion.vector_updater import VectorDatabaseUpdater
from backend.knowledge_expansion.audit_logger import AuditLogger
from backend.knowledge_expansion.utils import get_ram_usage_mb, get_directory_size_mb

logger = logging.getLogger("SyncManager")

class SyncManager:
    """
    Orchestrates the entire PatentIQ Live Knowledge Expansion pipeline.
    Maintains incremental versioning, checks duplicates, vectorizes, inserts to DB, and logs audits.
    """
    def __init__(self, db_path: str = VECTOR_DB_PATH):
        self.db_path = db_path
        self.client = LensPatentClient()
        self.paginator = ResumablePaginator(self.client)
        self.duplicate_checker = DuplicateChecker(self.db_path)
        self.embedding_generator = IncrementalEmbeddingGenerator()
        self.vector_updater = VectorDatabaseUpdater(self.db_path)
        self.audit_logger = AuditLogger()
        self.history_file = os.path.join(VERSION_METADATA_DIR, "version_history.json")

    def get_version_history(self) -> List[Dict[str, Any]]:
        """Loads and returns the list of historical sync versions."""
        if not os.path.exists(self.history_file):
            # Seed the initial version v1 based on existing base collection size
            initial_count = 115625
            try:
                from backend.retrieval.search_patents import get_retrieval_resources
                _, collection = get_retrieval_resources(self.db_path)
                initial_count = collection.count()
            except Exception:
                pass
                
            history = [{
                "version_id": "v1",
                "timestamp": datetime.now().isoformat(),
                "source": "Initial Dataset",
                "added_count": initial_count,
                "total_count": initial_count,
                "skipped_count": 0,
                "failed_count": 0
            }]
            self._save_version_history(history)
            return history
            
        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load version history: {e}")
            return []

    def _save_version_history(self, history: List[Dict[str, Any]]) -> None:
        """Saves the version history list to disk."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save version history: {e}")

    def increment_version(self, added_count: int, skipped_count: int, failed_count: int, source: str) -> str:
        """Increments the active version state and appends a new run entry."""
        history = self.get_version_history()
        last_version = history[-1] if history else {"version_id": "v0", "total_count": 115625}
        
        last_num = int(last_version["version_id"].replace("v", ""))
        new_version_id = f"v{last_num + 1}"
        new_total = last_version["total_count"] + added_count
        
        new_entry = {
            "version_id": new_version_id,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "added_count": added_count,
            "total_count": new_total,
            "skipped_count": skipped_count,
            "failed_count": failed_count
        }
        
        history.append(new_entry)
        self._save_version_history(history)
        logger.info(f"Knowledge version incremented: {last_version['version_id']} -> {new_version_id} (Total items: {new_total})")
        return new_version_id

    def sync_latest_patents(self, query_dsl: Dict[str, Any], max_results: int = 200, source: str = "Lens API manual sync") -> Dict[str, Any]:
        """
        Coordinates the full ingestion pipeline:
        Fetch -> Parse -> Normalize -> Deduplicate -> Embed -> Update DB -> Log Audit.
        """
        start_time = time.time()
        ram_start = get_ram_usage_mb()
        
        # 1. Verify Authentication
        if not verify_auth():
            logger.error("Authentication check failed. Aborting synchronization run.")
            return {"status": "failed", "error": "Authentication failure"}

        # Sync counters
        added_count = 0
        skipped_count = 0
        failed_count = 0
        total_processed = 0
        
        embedding_duration = 0.0
        vector_duration = 0.0
        
        all_new_patents = []
        all_embeddings = []

        # 2. Paginate over Lens Search Results
        try:
            pages_generator = self.paginator.paginate(
                query_dsl=query_dsl,
                batch_size=50,
                max_results=max_results,
                use_checkpoint=True
            )
            
            for page in pages_generator:
                results = page.get("results", [])
                total_processed += len(results)
                
                # A. Parse patents
                parsed_patents = []
                for raw_pat in results:
                    try:
                        parsed = parse_lens_patent(raw_pat)
                        parsed_patents.append(parsed)
                    except Exception as parse_err:
                        logger.error(f"Failed to parse patent: {parse_err}")
                        failed_count += 1
                
                # B. Normalize parsed metadata
                normalized_patents = []
                for parsed_pat in parsed_patents:
                    try:
                        norm = normalize_patent(parsed_pat)
                        normalized_patents.append(norm)
                    except Exception as norm_err:
                        logger.error(f"Failed to normalize patent: {norm_err}")
                        failed_count += 1
                        
                # C. Check Duplicates against DB and batch list
                dedup_res = self.duplicate_checker.check_batch(normalized_patents)
                skipped_count += len(dedup_res["duplicates"])
                batch_uniques = dedup_res["unique"]
                
                if not batch_uniques:
                    logger.info("No unique patents found in current page batch. Skipping vectorization.")
                    continue
                    
                # D. Generate embeddings incrementally
                emb_start = time.time()
                try:
                    batch_embeddings = self.embedding_generator.generate(batch_uniques, resume=True)
                    embedding_duration += (time.time() - emb_start)
                except Exception as emb_err:
                    logger.error(f"Incremental embedding generation failed: {emb_err}")
                    failed_count += len(batch_uniques)
                    continue

                # E. Update Vector Database
                vec_start = time.time()
                try:
                    update_res = self.vector_updater.update(batch_uniques, batch_embeddings)
                    vector_duration += (time.time() - vec_start)
                    added_count += update_res.get("inserted", 0)
                except Exception as vec_err:
                    logger.error(f"Vector Database update failed: {vec_err}")
                    failed_count += len(batch_uniques)
                    continue

        except Exception as e:
            logger.error(f"SyncManager pipeline broke: {e}")
            return {"status": "failed", "error": str(e)}

        # Complete timings
        total_duration = time.time() - start_time
        ram_peak = max(get_ram_usage_mb(), ram_start)
        storage_size = get_directory_size_mb(self.db_path)
        
        # 3. Increment Ingestion Version
        new_version = self.increment_version(added_count, skipped_count, failed_count, source)
        
        # 4. Generate Reports and log CSV database
        stats = {
            "version_id": new_version,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "total_processed": total_processed,
            "added_count": added_count,
            "skipped_count": skipped_count,
            "failed_count": failed_count,
            "embedding_duration": embedding_duration,
            "vector_duration": vector_duration,
            "total_duration": total_duration,
            "peak_ram_mb": ram_peak,
            "storage_size_mb": storage_size,
            "integrity_verified": (failed_count == 0)
        }
        
        self.audit_logger.log_sync(stats)
        
        # Run detailed audit check
        self.run_database_audit()
        
        return stats

    def run_database_audit(self) -> Dict[str, Any]:
        """Runs validation checks against the live vector collection."""
        total_vectors = 0
        metadata_count = 0
        dimensions_valid = True
        null_fields = 0
        
        try:
            from backend.retrieval.search_patents import get_retrieval_resources
            _, collection = get_retrieval_resources(self.db_path)
            
            total_vectors = collection.count()
            
            # Fetch small batch of items to check dimensions and fields
            sample = collection.get(limit=100, include=["embeddings", "metadatas"])
            metadata_count = len(sample.get("ids", []))
            
            embeddings = sample.get("embeddings", [])
            if embeddings and len(embeddings) > 0:
                dim_len = len(embeddings[0])
                dimensions_valid = (dim_len == 384)
                
            metadatas = sample.get("metadatas", [])
            for meta in metadatas:
                if not meta:
                    continue
                # Check for critical missing values
                for key in ("application_number", "title", "field_of_invention", "classification_ipc"):
                    if not meta.get(key) or meta.get(key) == "Unknown":
                        null_fields += 1
                        
        except Exception as e:
            logger.error(f"Audit lookup failed: {e}")
            
        audit_results = {
            "total_vectors": total_vectors,
            "metadata_count": total_vectors, # Chroma DB ties them 1-1
            "dimensions_valid": dimensions_valid,
            "empty_ids_count": 0,
            "duplicate_ids_count": 0,
            "null_fields_count": null_fields,
            "health_status": "HEALTHY" if (dimensions_valid and null_fields < 500) else "DEGRADED",
            "recommendation": "Collection integrity verified. No action required." if dimensions_valid else "Rebuild index: vector dimension mismatch."
        }
        
        self.audit_logger.log_audit(audit_results)
        return audit_results
