from backend.api.services.vector_store import ChromaVectorStore
from backend.api.services.orchestrator import PatentIntelligenceService

# Singleton instances for local run to cache model loads and db clients
_vector_store = ChromaVectorStore()
_patent_service = PatentIntelligenceService(_vector_store)

def get_vector_store() -> ChromaVectorStore:
    """
    Dependency injector for VectorStore.
    """
    return _vector_store

def get_patent_service() -> PatentIntelligenceService:
    """
    Dependency injector for PatentIntelligenceService.
    """
    return _patent_service
