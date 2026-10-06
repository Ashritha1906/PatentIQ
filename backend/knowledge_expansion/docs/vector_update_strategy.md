# Vector Database Update Strategy

This document outlines the database update strategy, indexing checks, and vector abstractions.

## Decoupled Architecture

PatentIQ decouples business logic from concrete databases using the `VectorStore` abstract base class.
Currently, `ChromaVectorStore` implements:
- `search(query, top_k, filters)`
- `insert(ids, documents, metadatas, embeddings)`
- `delete(ids)`

This ensures that if we migrate to Qdrant or Milvus in the future, we only need to write a new subclass implementing `VectorStore` without modifying the core sync manager or RAG pipelines.

## Incremental Updates (No Index Rebuilds)

Rebuilding vector indexes (which contain over 115,000 documents) on every sync is highly inefficient. 
Our strategy executes incremental database updates:
1. Filters out duplicate IDs via `DuplicateChecker` before encoding.
2. Generates new embeddings.
3. Appends new nodes directly using `ChromaVectorStore.insert()`.
4. Executes integrity validations: checks that `collection.count() == count_before + len(new_patents)`.

## Metadata Storage Schema

For each inserted document, ChromaDB indexes these exact metadata keys:
- `application_number` (string)
- `title` (string)
- `field_of_invention` (string)
- `classification_ipc` (string)
- `applicant_name` (string)

This ensures search query filters (applicant names, technology domain classes) can be applied directly in Chroma during retrieval.
