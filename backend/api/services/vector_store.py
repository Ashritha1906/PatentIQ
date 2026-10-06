import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger("VectorStore")

class VectorStore(ABC):
    """
    Abstract Base Class for Vector Store interactions.
    This defines the standard interface that our API uses, decoupling the business
    logic from the concrete database implementation.
    """
    @abstractmethod
    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        field_filter: Optional[str] = None, 
        ipc_filter: Optional[str] = None, 
        applicant_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for semantically similar items matching optional metadata filters.
        """
        pass

    @abstractmethod
    def insert(
        self, 
        ids: List[str], 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> None:
        """
        Insert documents and their embeddings into the store.
        """
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """
        Delete documents by their unique identifiers.
        """
        pass


class ChromaVectorStore(VectorStore):
    """
    Concrete implementation of VectorStore using ChromaDB.
    Reuses existing hybrid search and resource management modules.
    """
    def __init__(self, db_path: str = "data/vectordb"):
        self.db_path = db_path

    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        field_filter: Optional[str] = None, 
        ipc_filter: Optional[str] = None, 
        applicant_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # Import hybrid_search inside the method to support lazy-loading
        from backend.retrieval.hybrid_search import hybrid_search
        logger.info(f"ChromaVectorStore: executing search for query '{query[:50]}' with filters Field={field_filter}, IPC={ipc_filter}, Applicant={applicant_filter}")
        return hybrid_search(
            query=query,
            top_k=top_k,
            field_filter=field_filter,
            ipc_filter=ipc_filter,
            applicant_filter=applicant_filter,
            db_path=self.db_path
        )

    def insert(
        self, 
        ids: List[str], 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> None:
        from backend.retrieval.search_patents import get_retrieval_resources
        logger.info(f"ChromaVectorStore: inserting {len(ids)} documents")
        _, collection = get_retrieval_resources(self.db_path)
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def delete(self, ids: List[str]) -> None:
        from backend.retrieval.search_patents import get_retrieval_resources
        logger.info(f"ChromaVectorStore: deleting {len(ids)} documents")
        _, collection = get_retrieval_resources(self.db_path)
        collection.delete(ids=ids)
