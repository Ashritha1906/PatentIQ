# Ingestion Synchronization Workflow

This document details the step-by-step pipeline execution sequence during a knowledge expansion sync.

## Ingestion Workflow Sequence

```
[Start Manual / Scheduled Sync]
              │
              ▼
    [1. Check API Key validity] ── (Fail) ──➔ [Abort Run]
              │
           (Success)
              │
              ▼
    [2. Paginate over Lens Results]
              │
     (Read page chunk)
              │
              ▼
    [3. Parse raw JSON entries] ──➔ [Map technology fields]
              │
              ▼
    [4. Clean metadata & Applicants]
              │
              ▼
    [5. Filter existing document IDs] ──➔ [Skip Duplicates]
              │
              ▼
    [6. Generate Embeddings (all-MiniLM-L6-v2)]
              │
              ▼
    [7. Insert vectors and metadatas to ChromaDB]
              │
              ▼
    [8. Save Checkpoint (offset index)]
              │
        (Loop pages)
              │
     (Completion of all pages)
              │
              ▼
    [9. Increment Version (e.g., v1 -> v2)]
              │
              ▼
    [10. Generate Audit Reports & csv history]
              │
              ▼
          [Finish]
```

## Checkpoint Saving & Resumability

If the ingestion process is interrupted, the paginator writes intermediate states into `data/processed/versions/sync_checkpoint.json`.
On the next manual run, the system:
1. Locates the JSON file.
2. Checks that the query parameters match.
3. Loads the last successful offset `from_idx`.
4. Starts the request query at the saved offset to avoid double-downloading.
