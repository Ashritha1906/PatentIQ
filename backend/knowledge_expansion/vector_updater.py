import logging
from typing import List, Dict, Any
from backend.api.services.vector_store import ChromaVectorStore
from backend.knowledge_expansion.config import VECTOR_DB_PATH

logger = logging.getLogger("VectorUpdater")

class VectorUpdaterError(Exception):
    """Exception raised when Vector Database update operations fail."""
    pass

class VectorDatabaseUpdater:
    """
    Appends new patent records and their vector weights to ChromaDB.
    Verifies index alignments and checks database collection growth.
    """
    def __init__(self, db_path: str = VECTOR_DB_PATH):
        self.db_path = db_path
        self.vector_store = ChromaVectorStore(db_path=self.db_path)
        self._collection = None

    def _get_collection(self) -> Any:
        """Helper to fetch lazy-loaded raw collection reference for validation checkups."""
        if self._collection is None:
            try:
                from backend.retrieval.search_patents import get_retrieval_resources
                _, collection = get_retrieval_resources(self.db_path)
                self._collection = collection
            except Exception as e:
                logger.error(f"Failed to access ChromaDB collection: {e}")
        return self._collection

    def update(self, patents: List[Dict[str, Any]], embeddings: List[List[float]]) -> Dict[str, Any]:
        """
        Appends documents and embeddings to ChromaDB.
        Verifies insert alignment and returns validation stats.
        """
        if len(patents) != len(embeddings):
            raise VectorUpdaterError(
                f"Count mismatch: {len(patents)} patents given but {len(embeddings)} embeddings provided."
            )

        if not patents or not embeddings:
            return {"inserted": 0, "status": "no-op"}

        collection = self._get_collection()
        if not collection:
            raise VectorUpdaterError("ChromaDB collection resource is not accessible.")

        # Get count before insert
        count_before = collection.count()
        logger.info(f"Vector Database count before insertion: {count_before}")

        # Prepare payload datasets
        ids = [p["application_number"] for p in patents]
        documents = [p["patent_text"] for p in patents]
        
        # Select target metadata keys aligned with standard database schema
        metadatas = []
        for p in patents:
            metadatas.append({
                "application_number": p["application_number"],
                "title": p.get("title", "Unknown Title"),
                "field_of_invention": p.get("field_of_invention", "Unknown Field"),
                "classification_ipc": p.get("classification_ipc", "Unknown IPC"),
                "applicant_name": p.get("applicant_name", "Unknown Applicant")
            })

        logger.info(f"Appending {len(ids)} vectors to ChromaDB collection...")
        
        # Execute insert via VectorStore abstraction
        try:
            self.vector_store.insert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
        except Exception as e:
            logger.error(f"ChromaDB insert failed: {e}")
            raise VectorUpdaterError(f"ChromaDB insert execution failed: {e}")

        # Get count after insert for integrity check
        count_after = collection.count()
        expected_count = count_before + len(ids)
        
        logger.info(f"Vector Database count after insertion: {count_after}")
        
        integrity_ok = (count_after == expected_count)
        if not integrity_ok:
            logger.warning(
                f"Integrity check failed: expected total {expected_count} but Chroma reports {count_after}."
            )
            # Find out if some IDs were duplicates and thus updated/skipped by Chroma
            actual_increase = count_after - count_before
            logger.warning(f"Actual collection increase: {actual_increase} (expected {len(ids)}).")
        else:
            logger.info("ChromaDB index integrity check: SUCCESS.")

        return {
            "inserted": len(ids),
            "count_before": count_before,
            "count_after": count_after,
            "integrity_verified": integrity_ok,
            "status": "success"
        }
