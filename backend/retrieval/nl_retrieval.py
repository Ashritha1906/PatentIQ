import os
import re
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set

from backend.retrieval.search_patents import get_retrieval_resources
from backend.retrieval.identifier_normalizer import normalize_patent_identifier
from backend.retrieval.query_model import (
    PatentQuery,
    QueryIntent,
    PatentSearchResult,
    NLSearchResponse
)
from backend.llm.query_understanding import plan_patent_query

logger = logging.getLogger("NaturalLanguageRetrieval")

# Top-K Control parameters (Step 14)
QUERY_CANDIDATE_K = int(os.getenv("QUERY_CANDIDATE_K", "50"))
FINAL_RESULT_K = int(os.getenv("FINAL_RESULT_K", "20"))
RAG_CONTEXT_K = int(os.getenv("RAG_CONTEXT_K", "5"))

# Hybrid weight balance (Step 11)
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT", "0.65"))
KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT", "0.35"))

def normalize_scores(scores: List[float]) -> List[float]:
    """
    Step 11: Normalizes a list of arbitrary-scale scores to [0.0, 1.0] using Min-Max scaling.
    """
    if not scores:
        return []
    s_min = float(min(scores))
    s_max = float(max(scores))
    
    if s_max == s_min:
        # Uniform distribution: give a neutral 0.5 or 1.0 if positive
        return [1.0 if s_max > 0 else 0.0 for _ in scores]
        
    return [(s - s_min) / (s_max - s_min) for s in scores]

def compute_keyword_relevance(
    doc_title: str,
    doc_text: str,
    technical_concepts: List[str],
    search_phrases: List[str],
    expanded_terms: List[str]
) -> Tuple[float, List[str]]:
    """
    Step 10 & 13: Computes keyword matching score and extracts explainable match reasons.
    """
    title_lower = (doc_title or "").lower()
    text_lower = (doc_text or "").lower()
    reasons = []
    raw_score = 0.0
    
    # 1. Title matches (highest signal)
    for concept in technical_concepts:
        c_low = concept.lower().strip()
        if c_low and c_low in title_lower:
            raw_score += 5.0
            reasons.append(f"Title directly matches concept: '{concept}'")
        elif c_low and c_low in text_lower:
            raw_score += 2.0
            
    # 2. Search phrase exact matches
    for phrase in search_phrases:
        clean_p = phrase.replace('"', '').lower().strip()
        if clean_p and clean_p in title_lower:
            raw_score += 4.0
            reasons.append(f"Title matches search phrase: '{phrase}'")
        elif clean_p and clean_p in text_lower:
            raw_score += 2.5
            reasons.append(f"Abstract/Claims match search phrase: '{phrase}'")
            
    # 3. Expanded synonyms match
    for term in expanded_terms:
        t_low = term.lower().strip()
        if t_low and t_low in title_lower:
            raw_score += 2.0
        elif t_low and t_low in text_lower:
            raw_score += 1.0

    return raw_score, reasons

def execute_nl_hybrid_search(
    query_input: Any,
    top_k: int = FINAL_RESULT_K,
    candidate_k: int = QUERY_CANDIDATE_K,
    db_path: str = "data/vectordb"
) -> NLSearchResponse:
    """
    Step 8-16: Core Natural Language Query Engine and Dual-Track Hybrid Retrieval pipeline.
    """
    # 1. Parse or accept structured PatentQuery
    if isinstance(query_input, PatentQuery):
        patent_query = query_input
    elif isinstance(query_input, str):
        patent_query = plan_patent_query(query_input)
    else:
        raise ValueError(f"Unsupported query type: {type(query_input)}")

    original_query = patent_query.original_query.strip()
    
    # Check for empty query
    if not original_query:
        return NLSearchResponse(
            query="",
            interpreted_query=patent_query,
            search_strategy={"type": "empty_query"},
            total_results=0,
            results=[],
            ranking_information={"status": "empty_query"},
            source_metadata={"corpus": "PatentIQ Indexed Corpus"},
            confidence_message="Please enter a valid natural-language invention or technology query."
        )

    # 2. Step 8: Embedding Query using existing all-MiniLM-L6-v2
    model, collection = get_retrieval_resources(db_path)
    
    # Formulate enriched query representation for dense vector search
    dense_query_text = original_query
    if patent_query.technical_concepts:
        # Augment with top technical concepts
        dense_query_text = f"{original_query} {' '.join(patent_query.technical_concepts[:3])}"
        
    query_embedding = model.encode(dense_query_text, convert_to_numpy=True).tolist()

    # 3. Step 9 & 15: Retrieve candidates from ChromaDB with optional soft pre-filtering
    # Build where clause if valid metadata constraints exist
    filters = []
    if patent_query.applicant_constraints:
        # If applicant constraint is present, try exact match if 1 applicant
        app_name = patent_query.applicant_constraints[0]
        filters.append({"applicant_name": app_name})
        
    where_clause = None
    if len(filters) == 1:
        where_clause = filters[0]
    elif len(filters) > 1:
        where_clause = {"$and": filters}

    # Step 14: Retrieve large candidate pool for fusion, deduplication, and re-ranking
    query_k = max(candidate_k, top_k * 3)
    
    results = None
    if where_clause:
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=query_k,
                where=where_clause,
                include=["metadatas", "documents", "distances"]
            )
        except Exception as e:
            logger.warning(f"Chroma where query failed: {e}. Falling back to unfiltered query.")
            results = None
            
    # Fallback to unfiltered query if filtered query gave 0 results or had no filters
    if not results or not results["ids"] or not results["ids"][0]:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=query_k,
            include=["metadatas", "documents", "distances"]
        )

    # Check for empty vector store
    if not results or not results["ids"] or not results["ids"][0]:
        return NLSearchResponse(
            query=original_query,
            interpreted_query=patent_query,
            search_strategy={"status": "no_results_in_corpus"},
            total_results=0,
            results=[],
            ranking_information={},
            source_metadata={"corpus": "PatentIQ Indexed Corpus"},
            confidence_message="No matching patents were found in the currently indexed knowledge base."
        )

    ids = results["ids"][0]
    metadatas = results["metadatas"][0]
    documents = results["documents"][0]
    distances = results["distances"][0]

    # 4. Step 10 & 12: Deduplicate candidates & compute keyword matching
    seen_ids: Set[str] = set()
    seen_titles: Set[str] = set()
    candidate_records = []
    
    for i in range(len(ids)):
        raw_id = ids[i]
        meta = metadatas[i] or {}
        title = meta.get("title", "Unknown Title")
        title_norm = title.strip().upper()
        
        # Deduplication by canonical application_number / publication_number and title
        if raw_id in seen_ids or title_norm in seen_titles:
            continue
        seen_ids.add(raw_id)
        seen_titles.add(title_norm)
        
        # Raw semantic similarity (cosine similarity = 1 - cosine distance)
        dist = distances[i]
        semantic_sim = max(0.0, min(1.0, 1.0 - dist))
        
        doc_text = documents[i] or ""
        
        # Step 10: Keyword score
        kw_score, reasons = compute_keyword_relevance(
            doc_title=title,
            doc_text=doc_text,
            technical_concepts=patent_query.technical_concepts,
            search_phrases=patent_query.search_phrases,
            expanded_terms=patent_query.expanded_terms
        )
        
        # Step 13: Add semantic similarity explanation
        if semantic_sim >= 0.70:
            reasons.insert(0, "Strong semantic similarity to invention query")
        elif semantic_sim >= 0.45:
            reasons.insert(0, "Moderate conceptual similarity to core technology")
        else:
            reasons.insert(0, "General technical alignment")
            
        # Step 7 & 13: Check classification match
        doc_ipc = meta.get("classification_ipc", "")
        for cand_ipc in patent_query.classification_candidates:
            if cand_ipc and cand_ipc in doc_ipc:
                reasons.append(f"Classified under candidate IPC: {cand_ipc}")
                kw_score += 3.0
                break
                
        # Step 15: Extract year and apply date constraints if present
        pub_year = None
        year_match = re.search(r'/(20\d{2})$', raw_id)
        if year_match:
            pub_year = int(year_match.group(1))
            
        date_penalty = False
        if patent_query.date_constraints and pub_year:
            after_y = patent_query.date_constraints.get("after")
            before_y = patent_query.date_constraints.get("before")
            if after_y and pub_year < after_y:
                date_penalty = True
            if before_y and pub_year > before_y:
                date_penalty = True
                
            if not date_penalty:
                reasons.append(f"Filed in target period: {pub_year}")

        id_info = normalize_patent_identifier(raw_id)
        candidate_records.append({
            "patent_id": id_info["publication_number"],
            "publication_number": id_info["publication_number"],
            "country": id_info["country"],
            "document_number": id_info["document_number"],
            "kind_code": id_info["kind_code"],
            "title": title,
            "abstract": doc_text[:500] if len(doc_text) > 500 else doc_text,
            "applicant": meta.get("applicant_name", "Unknown Applicant"),
            "inventors": None,
            "publication_date": f"{pub_year}-01-01" if pub_year else None,
            "classification": doc_ipc,
            "raw_semantic": semantic_sim,
            "raw_keyword": kw_score,
            "reasons": reasons,
            "date_penalty": date_penalty
        })

    if not candidate_records:
        return NLSearchResponse(
            query=original_query,
            interpreted_query=patent_query,
            search_strategy={"status": "empty_after_dedup"},
            total_results=0,
            results=[],
            ranking_information={},
            source_metadata={"corpus": "PatentIQ Indexed Corpus"},
            confidence_message="No highly relevant patents were found in the currently indexed knowledge base."
        )

    # 5. Step 11: Score Normalization
    raw_semantics = [c["raw_semantic"] for c in candidate_records]
    raw_keywords = [c["raw_keyword"] for c in candidate_records]
    
    norm_semantics = normalize_scores(raw_semantics)
    norm_keywords = normalize_scores(raw_keywords)

    # 6. Step 12 & 13: Hybrid Fusion & Re-ranking
    ranked_results: List[PatentSearchResult] = []
    
    for idx, cand in enumerate(candidate_records):
        s_norm = norm_semantics[idx]
        k_norm = norm_keywords[idx]
        
        # Weighted hybrid score
        final_score = (SEMANTIC_WEIGHT * s_norm) + (KEYWORD_WEIGHT * k_norm)
        
        # Soft date constraint adjustment
        if cand["date_penalty"]:
            final_score *= 0.75
            
        final_score = float(round(max(0.0, min(1.0, final_score)), 4))
        
        # Format ranking reasons
        clean_reasons = list(dict.fromkeys(cand["reasons"]))[:4]

        res = PatentSearchResult(
            patent_id=cand["patent_id"],
            publication_number=cand["publication_number"],
            title=cand["title"],
            abstract=cand["abstract"],
            applicant=cand["applicant"],
            inventors=cand["inventors"],
            publication_date=cand["publication_date"],
            country=cand.get("country", "IN"),
            document_number=cand.get("document_number", cand["publication_number"]),
            kind_code=cand.get("kind_code", "A"),
            classification=cand["classification"],
            semantic_score=float(round(s_norm, 4)),
            keyword_score=float(round(k_norm, 4)),
            final_score=final_score,
            ranking_reasons=clean_reasons,
            source="PatentIQ Indexed Corpus (IPO)",
            source_url=f"https://ipindiaservices.gov.in/publicsearch"
        )
        ranked_results.append(res)

    # Sort descending by final hybrid score
    ranked_results.sort(key=lambda x: x.final_score, reverse=True)
    
    # Step 14: Top-K slice
    final_patents = ranked_results[:top_k]

    # Step 19: Confidence message if scores are low
    top_score = final_patents[0].final_score if final_patents else 0.0
    confidence_msg = None
    if top_score < 0.25:
        confidence_msg = "Notice: The retrieved patents have relatively weak overlap with the query. Consider refining or broadening technical terms."

    return NLSearchResponse(
        query=original_query,
        interpreted_query=patent_query,
        search_strategy={
            "retrieval_mode": "hybrid_semantic_keyword",
            "semantic_weight": SEMANTIC_WEIGHT,
            "keyword_weight": KEYWORD_WEIGHT,
            "candidate_pool_size": len(candidate_records),
            "final_k": len(final_patents)
        },
        total_results=len(final_patents),
        results=final_patents,
        ranking_information={
            "top_score": top_score,
            "semantic_weight": SEMANTIC_WEIGHT,
            "keyword_weight": KEYWORD_WEIGHT,
            "normalization": "min_max_scaling"
        },
        source_metadata={
            "corpus": "PatentIQ Indexed Indian Patent Dataset (2010-2019)",
            "total_indexed": 115625,
            "vector_space": "all-MiniLM-L6-v2 (Cosine)"
        },
        confidence_message=confidence_msg
    )
