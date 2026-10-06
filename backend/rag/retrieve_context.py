import logging
from backend.llm.query_understanding import understand_query
from backend.retrieval.hybrid_search import hybrid_search

logger = logging.getLogger("RetrieveContext")

def retrieve_patent_context(user_idea, top_k=10, db_path="data/vectordb"):
    """
    Executes RAG orchestration: Understands query -> Queries ChromaDB -> Deduplicates results -> Returns context.
    """
    # 1. Understand user idea
    logger.info(f"Analyzing user idea: '{user_idea[:50]}...'")
    query_params = understand_query(user_idea)
    
    optimized_query = query_params.get("optimized_query", user_idea)
    hints = query_params.get("metadata_hints", {})
    
    field_filter = hints.get("field_of_invention")
    applicant_filter = hints.get("applicant_name")
    
    # 2. Query vector database (retrieving larger pool for deduplication)
    logger.info(f"Searching ChromaDB with optimized query: '{optimized_query[:50]}'...")
    raw_results = hybrid_search(
        query=optimized_query,
        top_k=top_k * 2,  # Retrieve double for deduplication
        field_filter=field_filter,
        applicant_filter=applicant_filter,
        db_path=db_path
    )
    
    # 3. Deduplicate and Rank
    seen_titles = set()
    seen_app_nums = set()
    deduped_results = []
    
    for res in raw_results:
        app_num = res["application_number"]
        title_normalized = res["title"].strip().upper()
        
        # Deduplicate based on ID and Title
        if app_num in seen_app_nums or title_normalized in seen_titles:
            continue
            
        seen_titles.add(title_normalized)
        seen_app_nums.add(app_num)
        deduped_results.append(res)
        
        # Stop once we have top_k results
        if len(deduped_results) >= top_k:
            break
            
    logger.info(f"Retrieved {len(deduped_results)} unique patents for RAG context.")
    return {
        "query_understanding": query_params,
        "retrieved_patents": deduped_results
    }
