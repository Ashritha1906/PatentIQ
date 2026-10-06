import os
import sys
import chromadb
from backend.retrieval.search_patents import get_retrieval_resources

"""
================================================================================
HYBRID SEARCH ARCHITECTURAL ANALYSIS
================================================================================

Advantages:
1. Search Precision: Combines the power of vector search (conceptual meaning) with hard constraints
   (e.g., specific technology fields or assignees), preventing irrelevant results.
2. Latency Optimization: Performing pre-filtering in ChromaDB limits the search space for the 
   approximate nearest neighbor (HNSW) graph traversal, reducing query times for very large datasets.
3. Logical Domain isolation: Ensures queries on "communication" return communication patents, even 
   if the query contains highly generic tech jargon (e.g. "software optimization").

Limitations:
1. Exact String Constraint: ChromaDB's built-in `where` dictionary utilizes strict equality operators. 
   Sub-string or prefix wildcard matches (e.g. searching "H04L*" prefix for IPC code H04L 29/06) 
   are not supported natively out-of-the-box.
2. Casing Variations: Mismatched cases (e.g., "Qualcomm Incorporated" vs "QUALCOMM INCORPORATED") 
   will cause the filter to fail and return zero results.
3. Sparsity / Over-filtering: Strict `$and` logic combination of metadata filters can easily shrink 
   the candidate pool to zero if the constraints are too tight, returning empty queries.

Performance Tradeoffs:
1. Pre-Filtering (Chroma-level):
   - Tradeoff: Faster runtime but requires exact structural matches. If no patents match the hard filter, 
     zero results are returned, ignoring highly similar patents that are slightly misclassified.
2. Post-Filtering (Python-level):
   - Tradeoff: More flexible (supports case-insensitivity and sub-string matches) but requires retrieving 
     a larger Top-K pool (e.g. Top-100) and filtering them in memory, which increases latency and 
     risk of dropping highly relevant patents if they fall outside the initial retrieval window.
================================================================================
"""

def hybrid_search(query, top_k=5, field_filter=None, ipc_filter=None, applicant_filter=None, db_path="data/vectordb"):
    """
    Performs hybrid search combining semantic query embedding with metadata pre-filters.
    Filters:
      - field_filter: matches 'field_of_invention'
      - ipc_filter: matches 'classification_ipc'
      - applicant_filter: matches 'applicant_name'
    """
    model, collection = get_retrieval_resources(db_path)
    
    # 1. Generate Query Embedding
    query_embedding = model.encode(query, convert_to_numpy=True).tolist()
    
    # 2. Build ChromaDB Where Clause
    filters = []
    if field_filter:
        filters.append({"field_of_invention": field_filter})
    if ipc_filter:
        filters.append({"classification_ipc": ipc_filter})
    if applicant_filter:
        filters.append({"applicant_name": applicant_filter})
        
    where_clause = None
    if len(filters) == 1:
        where_clause = filters[0]
    elif len(filters) > 1:
        where_clause = {"$and": filters}
        
    # 3. Query ChromaDB with Filters (with fallback if 0 results found)
    import logging
    logger = logging.getLogger("HybridSearch")
    
    results = None
    if where_clause:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["metadatas", "documents", "distances"]
        )
        if not results or not results["ids"] or not results["ids"][0]:
            logger.info("No results found with metadata filters. Falling back to unfiltered semantic search...")
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["metadatas", "documents", "distances"]
            )
    else:
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
    if len(sys.argv) < 2:
        print("Usage: python hybrid_search.py \"<query>\" [--field <field>] [--ipc <ipc>] [--applicant <applicant>] [--top_k <k>]")
        sys.exit(0)
        
    query = sys.argv[1]
    
    import argparse
    parser = argparse.ArgumentParser(description="PatentIQ - Hybrid Search CLI Interface")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--field", type=str, default=None, help="Filter by Invention Field")
    parser.add_argument("--ipc", type=str, default=None, help="Filter by IPC Classification code")
    parser.add_argument("--applicant", type=str, default=None, help="Filter by Applicant Name")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results")
    
    # We parse manually to prevent argument conflict if run directly
    args, unknown = parser.parse_known_args()
    
    print(f"Hybrid Search Query: '{args.query}'")
    print(f"Filters: Field={args.field}, IPC={args.ipc}, Applicant={args.applicant} (top_k={args.top_k})\n")
    
    try:
        results = hybrid_search(
            args.query, 
            top_k=args.top_k, 
            field_filter=args.field, 
            ipc_filter=args.ipc, 
            applicant_filter=args.applicant
        )
    except Exception as e:
        print(f"[ERROR] Hybrid search failed: {e}")
        sys.exit(1)
        
    print(f"Retrieved {len(results)} Patents:")
    print("==================================================")
    for i, res in enumerate(results):
        print(f"{i+1}. Title: {res['title']}")
        print(f"   Score: {res['similarity_score']:.4f} (Distance: {res['distance']:.4f})")
        print(f"   Applicant: {res['applicant_name']} | Field: {res['field_of_invention']} | IPC: {res['classification_ipc']}")
        print("--------------------------------------------------")

if __name__ == '__main__':
    main()
