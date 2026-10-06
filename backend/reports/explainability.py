import logging

logger = logging.getLogger("Explainability")

def generate_explainability_traces(retrieved_patents, query_understanding_params):
    """
    Generates explainability traces mapping why each patent was retrieved,
    showing matched keywords, distance metrics, and category alignments.
    """
    query_keywords = set(k.lower() for k in query_understanding_params.get("keywords", []))
    query_domain = query_understanding_params.get("technology_domain", "UNKNOWN").upper()
    
    traces = {}
    for idx, pat in enumerate(retrieved_patents):
        app_num = pat["application_number"]
        title = pat["title"]
        field = pat["field_of_invention"]
        similarity = pat["similarity_score"]
        
        # Calculate matched keywords (intersection of query keywords and title/field words)
        patent_words = set(re_split_words(title.lower() + " " + field.lower()))
        matched_keywords = query_keywords.intersection(patent_words)
        
        # Identify alignment
        domain_alignment = "EXACT" if field.upper() == query_domain else (
            "HIGH" if (query_domain in field.upper() or field.upper() in query_domain) else "MEDIUM"
        )
        
        reason = (
            f"Retrieved due to strong semantic conceptual similarity (cosine score: {similarity:.4f}). "
            f"Shares matching technical concepts in the field of {field}."
        )
        
        traces[app_num] = {
            "title": title,
            "matched_concepts": list(matched_keywords),
            "similarity_score": similarity,
            "technology_alignment": domain_alignment,
            "reason_retrieved": reason
        }
        
    return traces

def re_split_words(text):
    """
    Helper to extract alphanumeric words.
    """
    import re
    return re.findall(r'\b\w+\b', text)
