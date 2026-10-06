import os
import sys
import time
import numpy as np
import pandas as pd
import chromadb

def main():
    print("==================================================")
    print("PatentIQ - Ingesting Embeddings into ChromaDB")
    print("==================================================")

    # File paths
    embeddings_path = os.path.join("data", "processed", "patent_embeddings.npy")
    dataset_path = os.path.join("data", "processed", "patent_text_dataset.csv")
    db_path = os.path.join("data", "vectordb")

    # Check source assets
    if not os.path.exists(embeddings_path) or not os.path.exists(dataset_path):
        print("[ERROR] Required pre-computed assets not found.")
        print("Please run building of patent text and embeddings first.")
        sys.exit(1)

    # Load assets
    print("Loading pre-computed embeddings and dataset...")
    embeddings = np.load(embeddings_path)
    df = pd.read_csv(dataset_path)
    total_records = len(df)
    
    if len(embeddings) != total_records:
        print(f"[ERROR] Mismatch between embeddings size ({len(embeddings)}) and dataset rows ({total_records}).")
        sys.exit(1)
        
    print(f"Loaded {total_records} records successfully.")

    # Initialize ChromaDB persistent client
    print(f"Initializing persistent ChromaDB client at: {db_path}")
    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)

    # Get or create collection
    # Note: ChromaDB defaults to L2 distance. L2 is fine for normalized vectors (cosine similarity = 1 - L2/2).
    # Since our embeddings are L2 normalized (average norm is 1.0), L2 or Cosine distance are mathematically equivalent in sorting order.
    # We can explicitly set space to "cosine" inside metadata parameters for clarity if we want:
    collection = client.get_or_create_collection(
        name="patentiq_patents",
        metadata={"hnsw:space": "cosine"}
    )

    # Check current state for checkpoint recovery
    current_count = collection.count()
    if current_count > 0:
        print(f"[RESUME] Found existing database containing {current_count} documents.")
        if current_count >= total_records:
            print("[INFO] All records are already ingested. Nothing to do.")
            print("==================================================")
            sys.exit(0)
        start_idx = current_count
    else:
        print("Starting new collection ingestion.")
        start_idx = 0

    # Batch insertion configuration
    batch_size = 5000  # Safe batch size to prevent SQLite parameter limits and memory spikes
    num_batches = int(np.ceil((total_records - start_idx) / batch_size))
    
    print(f"Ingesting remaining {total_records - start_idx} records in batches of {batch_size}...")
    start_total_time = time.time()
    
    for batch_num in range(num_batches):
        batch_start_idx = start_idx + (batch_num * batch_size)
        batch_end_idx = min(batch_start_idx + batch_size, total_records)
        
        start_batch_time = time.time()
        
        # Prepare batch data
        batch_df = df.iloc[batch_start_idx:batch_end_idx].copy()
        
        # Ensure metadata is flat and handles NaNs safely
        metadatas = batch_df[[
            'application_number', 
            'title', 
            'field_of_invention', 
            'classification_ipc', 
            'applicant_name'
        ]].fillna("Unknown").to_dict(orient="records")
        
        ids = batch_df['application_number'].astype(str).tolist()
        documents = batch_df['patent_text'].astype(str).tolist()
        
        # Convert numpy slice of Float32 embeddings to regular list of float lists
        batch_embeddings = embeddings[batch_start_idx:batch_end_idx].tolist()
        
        # Ingest to ChromaDB
        try:
            collection.add(
                ids=ids,
                embeddings=batch_embeddings,
                metadatas=metadatas,
                documents=documents
            )
        except Exception as e:
            print(f"\n[ERROR] Ingestion failed at index {batch_start_idx} to {batch_end_idx}: {e}")
            sys.exit(1)
            
        batch_time = time.time() - start_batch_time
        speed = len(ids) / batch_time
        overall_progress = (batch_end_idx / total_records) * 100
        
        print(f"  Batch {batch_num + 1}/{num_batches} ({batch_start_idx} to {batch_end_idx}) completed in {batch_time:.2f}s ({speed:.2f} docs/sec) | Progress: {overall_progress:.2f}%")

    total_time = time.time() - start_total_time
    print(f"\nIngestion completed successfully in {total_time / 60:.2f} minutes.")
    print(f"Final collection count: {collection.count()}")
    print("==================================================")

if __name__ == '__main__':
    main()
