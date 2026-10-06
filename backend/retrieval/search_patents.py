import os
import sys
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer

# Global cache for lazy initialization
_model_cache = None
_collection_cache = None

def get_retrieval_resources(db_path="data/vectordb"):
    """
    Lazy loader for SentenceTransformer model and ChromaDB collection.
    """
    global _model_cache, _collection_cache
    
    if _model_cache is None:
        device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") or getattr(np, "__git_version__", None) is None else "cpu"
        # Let SentenceTransformer auto-detect device (CPU/GPU)
        _model_cache = SentenceTransformer('all-MiniLM-L6-v2')
        
    if _collection_cache is None:
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"ChromaDB persistent path does not exist: {db_path}")
        client = chromadb.PersistentClient(path=db_path)
        _collection_cache = client.get_collection("patentiq_patents")
        
    return _model_cache, _collection_cache

def semantic_search(query, top_k=5, db_path="data/vectordb"):
    """
    Performs pure semantic vector search against ChromaDB.
    Returns a list of dicts with similarity scores (1 - cosine distance).
    """
    model, collection = get_retrieval_resources(db_path)
    
    # 1. Embed query
    query_embedding = model.encode(query, convert_to_numpy=True).tolist()
    
    # 2. Query ChromaDB
    # Space is configured as cosine distance, so results["distances"][0] contains cosine distances (0.0 to 2.0)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "documents", "distances"]
    )
    
    formatted_results = []
    if not results or not results["ids"] or not results["ids"][0]:
        return formatted_results
        
    ids = results["ids"][0]
    metadatas = results["metadatas"][0]
    documents = results["documents"][0]
    distances = results["distances"][0]
    
    for i in range(len(ids)):
        # Calculate similarity score: cosine_similarity = 1 - cosine_distance
        distance = distances[i]
        similarity_score = 1.0 - distance
        
        meta = metadatas[i]
        formatted_results.append({
            "application_number": ids[i],
            "title": meta.get("title", "Unknown Title"),
            "similarity_score": float(similarity_score),
            "distance": float(distance),
            "field_of_invention": meta.get("field_of_invention", "Unknown Field"),
            "classification_ipc": meta.get("classification_ipc", "Unknown IPC"),
            "applicant_name": meta.get("applicant_name", "Unknown Applicant"),
            "patent_text": documents[i]
        })
        
    return formatted_results

def main():
    # Simple CLI test run if script is run directly
    if len(sys.argv) < 2:
        print("Usage: python search_patents.py \"<your search query>\" [top_k]")
        sys.exit(0)
        
    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print(f"Searching for: '{query}' (top_k={top_k})...\n")
    try:
        results = semantic_search(query, top_k=top_k)
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        sys.exit(1)
        
    print(f"Top {len(results)} Semantically Similar Patents:")
    print("==================================================")
    for i, res in enumerate(results):
        print(f"{i+1}. Title: {res['title']}")
        print(f"   Score: {res['similarity_score']:.4f} (Distance: {res['distance']:.4f})")
        print(f"   Applicant: {res['applicant_name']} | Field: {res['field_of_invention']} | IPC: {res['classification_ipc']}")
        print(f"   App Number: {res['application_number']}")
        print("--------------------------------------------------")

if __name__ == '__main__':
    main()
