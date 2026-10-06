import hashlib
import logging
from typing import List, Dict, Any, Set
from backend.knowledge_expansion.config import VECTOR_DB_PATH

logger = logging.getLogger("DuplicateChecker")

class DuplicateChecker:
    """
    Checks for duplicate patent records using application number lookups
    and MD5 content hashing of processed patent text representations.
    """
    def __init__(self, db_path: str = VECTOR_DB_PATH):
        self.db_path = db_path
        self._collection = None

    def _get_collection(self) -> Any:
        """Lazily load the Chroma collection reference."""
        if self._collection is None:
            try:
                from backend.retrieval.search_patents import get_retrieval_resources
                _, collection = get_retrieval_resources(self.db_path)
                self._collection = collection
            except Exception as e:
                logger.error(f"Failed to access ChromaDB collection: {e}")
        return self._collection

    def exists_in_db(self, application_number: str) -> bool:
        """Checks if an application number already exists as a document ID inside ChromaDB."""
        collection = self._get_collection()
        if not collection:
            return False
            
        try:
            # Query collection by IDs
            res = collection.get(ids=[application_number], include=[])
            return len(res.get("ids", [])) > 0
        except Exception as e:
            logger.error(f"ChromaDB lookup failed for {application_number}: {e}")
            return False

    def check_batch(self, patents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Processes a list of parsed patent dictionaries.
        Filters out duplicates existing in ChromaDB or inside the batch itself.
        Returns a dict containing 'unique' and 'duplicates' lists.
        """
        unique_patents = []
        duplicate_patents = []
        
        seen_batch_ids: Set[str] = set()
        seen_batch_hashes: Set[str] = set()

        for pat in patents:
            app_num = pat["application_number"]
            patent_text = pat.get("patent_text", "")
            
            # Generate MD5 content hash
            text_hash = hashlib.md5(patent_text.encode("utf-8")).hexdigest()
            
            is_dup = False
            dup_reason = ""
            
            # Check 1: Duplicate inside same batch
            if app_num in seen_batch_ids:
                is_dup = True
                dup_reason = "Application ID duplicate within batch"
            elif text_hash in seen_batch_hashes:
                is_dup = True
                dup_reason = "Content hash duplicate within batch"
            # Check 2: Duplicate inside DB
            elif self.exists_in_db(app_num):
                is_dup = True
                dup_reason = "Application ID already exists in ChromaDB"
                
            if is_dup:
                pat_copy = pat.copy()
                pat_copy["duplicate_reason"] = dup_reason
                duplicate_patents.append(pat_copy)
                logger.debug(f"Duplicate filtered: {app_num} ({dup_reason})")
            else:
                seen_batch_ids.add(app_num)
                seen_batch_hashes.add(text_hash)
                unique_patents.append(pat)

        logger.info(f"Deduplication complete: {len(unique_patents)} unique, {len(duplicate_patents)} duplicates identified.")
        return {
            "unique": unique_patents,
            "duplicates": duplicate_patents
        }
