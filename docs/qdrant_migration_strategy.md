# PatentIQ - Qdrant Vector Store Migration Strategy

This document outlines the roadmap, schema mapping, and code structures required to migrate PatentIQ's vector indexing database from ChromaDB to Qdrant.

---

## 1. Migration Benefits

Migrating to Qdrant offers significant production benefits:
- **Horizontal Scaling:** Qdrant is designed for distributed clustering, making it suitable for multi-node deployments with millions of patents.
- **Advanced Payload Filtering:** Support for full-text search, regex filtering, and range operations on metadata payloads.
- **Language Support:** Native gRPC API client support for high-throughput and low-latency database queries.

---

## 2. Decoupled Architecture

By implementing the `VectorStore` interface (Phase 5H), the backend business logic is completely insulated from database choices.

```
       [Orchestrator Service]
                 │
                 ▼ (Calls abstract methods: search, insert, delete)
      ┌─────────────────────┐
      │  VectorStore (ABC)  │
      └──────────┬──────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
[ChromaVectorStore]    [QdrantVectorStore] (Future Migration target)
  (ChromaDB Engine)     (Qdrant DB Engine)
```

---

## 3. Qdrant Migration Roadmap

### Phase 1: Infrastructure Setup
Start a persistent Qdrant instance via Docker:
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### Phase 2: Schema Mapping
Map ChromaDB records directly to Qdrant Points:

| ChromaDB Element | Qdrant Point Element | Type / Description |
| :--- | :--- | :--- |
| `id` | `id` | Unique UUID or Integer. Since Chroma uses patent application numbers (e.g. `1/CHE/2010`), these strings can be converted to UUIDs via namespace mapping (or hashed). |
| `embedding` | `vector` | List of Float32 dimensions (384 for `all-MiniLM-L6-v2`). |
| `metadata` | `payload` | Key-value dictionary containing: `title`, `applicant_name`, `field_of_invention`, `classification_ipc`. |
| `document` | `payload.patent_text` | Store the raw text directly in the payload under `patent_text`. |

### Phase 3: Implement Qdrant Wrapper
Create `backend/api/services/qdrant_store.py` extending `VectorStore`:

```python
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from backend.api.services.vector_store import VectorStore

class QdrantVectorStore(VectorStore):
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "patentiq_patents"):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        field_filter: Optional[str] = None, 
        ipc_filter: Optional[str] = None, 
        applicant_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # 1. Embed query
        query_vector = self.model.encode(query, convert_to_numpy=True).tolist()

        # 2. Compile Qdrant Match Filters
        must_filters = []
        if field_filter:
            must_filters.append(models.FieldCondition(
                key="field_of_invention",
                match=models.MatchValue(value=field_filter)
            ))
        if ipc_filter:
            must_filters.append(models.FieldCondition(
                key="classification_ipc",
                match=models.MatchValue(value=ipc_filter)
            ))
        if applicant_filter:
            must_filters.append(models.FieldCondition(
                key="applicant_name",
                match=models.MatchValue(value=applicant_filter)
            ))

        query_filter = models.Filter(must=must_filters) if must_filters else None

        # 3. Query Collection
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True
        )

        # 4. Format outputs to match standard dict layout
        formatted = []
        for res in results:
            payload = res.payload
            formatted.append({
                "application_number": payload.get("application_number"),
                "title": payload.get("title"),
                "similarity_score": float(res.score),
                "field_of_invention": payload.get("field_of_invention"),
                "classification_ipc": payload.get("classification_ipc"),
                "applicant_name": payload.get("applicant_name"),
                "patent_text": payload.get("patent_text")
            })
        return formatted

    def insert(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        points = []
        for i in range(len(ids)):
            # Generate deterministic UUID from application number
            pt_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, ids[i]))
            
            payload = metadatas[i].copy()
            payload["patent_text"] = documents[i]
            payload["application_number"] = ids[i]
            
            points.append(models.PointStruct(
                id=pt_id,
                vector=embeddings[i],
                payload=payload
            ))
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def delete(self, ids: List[str]) -> None:
        point_ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, app_id)) for app_id in ids]
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(points=point_ids)
        )
```

### Phase 4: Swap Injection Dependencies
Simply update the singleton initialization inside `backend/api/services/dependencies.py`:

```diff
-from backend.api.services.vector_store import ChromaVectorStore
+from backend.api.services.qdrant_store import QdrantVectorStore
 
-_vector_store = ChromaVectorStore()
+_vector_store = QdrantVectorStore(host="production-qdrant-cluster", port=6333)
 _patent_service = PatentIntelligenceService(_vector_store)
```

No other Python logic, routing schemas, or frontend codes require modification. The system remains fully operational throughout the database swap.
