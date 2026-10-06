# Incremental Embedding Strategy

This document details our approach to vector generation, minimizing recalculation costs and ensuring consistency with Phase 2.

## Embedding Model Configuration

- **Model:** `all-MiniLM-L6-v2` (via `sentence-transformers` library)
- **Embedding Size:** **384 dimensions** (dense float array)
- **Distance Metric:** Cosine similarity (configured in Chroma via `hnsw:space: cosine`)

## Text Representation Template

To maintain embedding compatibility with existing vectors, the text representations passed to the encoder are constructed using the canonical template:

```
Title: {title}

Field Of Invention: {field_of_invention}

IPC Classification: {classification_ipc}

Applicant: {applicant_name}
```

- If fields are missing after normalization, they fallback to `"Unknown"`.
- Cleaners strip double whitespaces, unicode control tags, and poorly escaped quotes.

## Optimization & Resumability

1. **Model Singleton:** The model is initialized once and stored globally (`get_embedding_model()`) to avoid loading weights into memory repeatedly across sync jobs.
2. **Incremental Batch Processing:** Vectors are generated in batches (default: `64`). In case of an interruption, intermediate embeddings lists are saved to `embeddings_checkpoint.npy` and reloaded to skip finished pages.
