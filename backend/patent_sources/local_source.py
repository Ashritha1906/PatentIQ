import logging
from typing import List, Dict, Any, Optional
from backend.patent_sources.base import PatentSource
from backend.retrieval.query_model import PatentSearchResult, PatentQuery
from backend.retrieval.nl_retrieval import execute_nl_hybrid_search
from backend.api.services.vector_store import ChromaVectorStore

logger = logging.getLogger("LocalPatentSource")

class LocalPatentSource(PatentSource):
    """
    Local PatentIQ provider wrapping the indexed 115,625-patent corpus
    (ChromaDB + BM25 hybrid search with all-MiniLM-L6-v2 embeddings).
    """

    def __init__(self, db_path: str = "data/vectordb"):
        self.db_path = db_path
        self._store: Optional[ChromaVectorStore] = None

    @property
    def name(self) -> str:
        return "LOCAL_PATENTIQ"

    def _get_store(self) -> ChromaVectorStore:
        if self._store is None:
            self._store = ChromaVectorStore(db_path=self.db_path)
        return self._store

    def search(
        self,
        query: str,
        concepts: Optional[List[str]] = None,
        top_k: int = 5,
        interpreted_query: Optional[PatentQuery] = None,
        **kwargs
    ) -> List[PatentSearchResult]:
        """
        Executes hybrid search against the local PatentIQ corpus.
        Preserves existing Phase 6A retrieval behavior and scoring.
        """
        try:
            results = execute_nl_hybrid_search(
                query=query,
                top_k=top_k,
                interpreted_query=interpreted_query,
                db_path=self.db_path,
                **kwargs
            )
            # Tag explicit source provenance
            for res in results:
                res.source = self.name
            return results
        except Exception as e:
            logger.error(f"LocalPatentSource search error: {e}", exc_info=True)
            return []

    def fetch_document(self, identifier: str) -> Optional[PatentSearchResult]:
        """
        Fetches single patent from the local vector store by identifier.
        """
        try:
            store = self._get_store()
            results = store.search(identifier, top_k=1)
            if results:
                raw = results[0]
                return PatentSearchResult(
                    patent_id=raw.get("patent_id", identifier),
                    publication_number=raw.get("publication_number", identifier),
                    title=raw.get("title", "Untitled"),
                    abstract=raw.get("abstract"),
                    applicant=raw.get("applicant"),
                    country=raw.get("country", "IN"),
                    document_number=raw.get("document_number", identifier),
                    kind_code=raw.get("kind_code"),
                    publication_date=raw.get("publication_date"),
                    source=self.name,
                    final_score=1.0,
                    ranking_reasons=["Direct identifier lookup in local corpus"]
                )
        except Exception as e:
            logger.warning(f"Local fetch_document error for {identifier}: {e}")
        return None

    def health_check(self) -> Dict[str, Any]:
        """
        Verifies local ChromaDB connectivity and record count.
        """
        try:
            from backend.retrieval.search_patents import get_retrieval_resources
            _, collection = get_retrieval_resources(self.db_path)
            count = collection.count()
            return {
                "status": "healthy",
                "provider": self.name,
                "record_count": count,
                "vector_store": "ChromaDB",
                "embeddings": "all-MiniLM-L6-v2"
            }
        except Exception as e:
            return {
                "status": "degraded",
                "provider": self.name,
                "error": str(e)
            }

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "source": self.name,
            "type": "Local Vector & Lexical Store",
            "jurisdiction": "Indian Patent Office (IPO)",
            "approximate_records": 115625,
            "hybrid_retrieval": True,
            "offline_capable": True
        }
