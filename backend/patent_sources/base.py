from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.retrieval.query_model import PatentSearchResult

class PatentSource(ABC):
    """
    Abstract base provider interface for patent knowledge sources.
    Supports both local corpus retrieval and live external patent repositories
    (e.g., EPO European Publication Server, and potential future sources like USPTO or Lens).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name for this patent source."""
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        concepts: Optional[List[str]] = None,
        top_k: int = 5,
        **kwargs
    ) -> List[PatentSearchResult]:
        """
        Executes search against this patent source and returns normalized PatentSearchResult objects.
        """
        pass

    @abstractmethod
    def fetch_document(self, identifier: str) -> Optional[PatentSearchResult]:
        """
        Fetches a single full patent document by its identifier if supported.
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Returns health and availability status for this provider.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns source metadata, coverage characteristics, and limits.
        """
        pass
