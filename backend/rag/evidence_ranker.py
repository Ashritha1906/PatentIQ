import logging

logger = logging.getLogger("EvidenceRanker")

# Domain mapping from Broad Category / Technology Domain to allowed DB Fields
DOMAIN_MAPPING = {
    "AI": ["COMPUTER SCIENCE", "ELECTRONICS", "ELECTRICAL", "COMMUNICATION", "PHYSICS"],
    "HEALTHCARE": ["BIO-MEDICAL ENGINEERING", "PHARMACEUTICALS", "PHYSICS", "MECHANICAL ENGINEERING", "GENERAL ENGINEERING"],
    "BIOTECHNOLOGY": ["BIOTECHNOLOGY", "MICRO BIOLOGY", "TRADITIONAL KNOWLEDGE BIOTECHNOLOGY", "PHARMACEUTICALS", "CHEMICAL"],
    "COMMUNICATION": ["COMMUNICATION", "ELECTRICAL", "ELECTRONICS", "COMPUTER SCIENCE"],
    "COMPUTER SCIENCE": ["COMPUTER SCIENCE", "ELECTRICAL", "ELECTRONICS", "COMMUNICATION"],
    "ELECTRONICS": ["ELECTRONICS", "ELECTRICAL", "COMPUTER SCIENCE", "PHYSICS"],
    "MECHANICAL ENGINEERING": ["MECHANICAL ENGINEERING", "GENERAL ENGINEERING", "CIVIL", "METALLURGY", "TEXTILE"],
    "ENERGY": ["ELECTRICAL", "PHYSICS", "CHEMICAL", "MECHANICAL ENGINEERING", "GENERAL ENGINEERING"],
    "AUTOMOTIVE": ["MECHANICAL ENGINEERING", "ELECTRICAL", "ELECTRONICS", "GENERAL ENGINEERING"],
    "CYBERSECURITY": ["COMPUTER SCIENCE", "ELECTRONICS", "COMMUNICATION", "ELECTRICAL"]
}

def check_domain_alignment(tech_domain, patent_field):
    """
    Checks if a patent's field of invention aligns with the query's technology domain.
    """
    if not tech_domain or not patent_field:
        return False
    
    tech_domain_upper = tech_domain.strip().upper()
    patent_field_upper = patent_field.strip().upper()
    
    # Check direct equality
    if tech_domain_upper == patent_field_upper:
        return True
        
    # Check allowed list
    allowed = DOMAIN_MAPPING.get(tech_domain_upper, [])
    if patent_field_upper in allowed:
        return True
        
    # Check substring match
    for domain, fields in DOMAIN_MAPPING.items():
        if domain in tech_domain_upper:
            if patent_field_upper in fields:
                return True
                
    return False

def rank_evidence(retrieved_patents, query_understanding):
    """
    Computes an Evidence Score (0-100) for each retrieved patent based on:
      - Semantic similarity (50% weight)
      - Concept/keyword coverage (20% weight)
      - Domain alignment (20% weight)
      - Metadata hints (IPC/Applicant) relevance (10% weight)
    Returns list of patents sorted by evidence score in descending order.
    """
    if not retrieved_patents:
        return []
        
    ranked_results = []
    keywords = [kw.lower() for kw in query_understanding.get("keywords", []) if len(kw) > 2]
    tech_domain = query_understanding.get("technology_domain", "")
    hints = query_understanding.get("metadata_hints", {})
    hint_applicant = hints.get("applicant_name", "") if hints else ""
    hint_ipc = hints.get("field_of_invention", "") if hints else "" # Or class code
    
    for pat in retrieved_patents:
        # 1. Semantic Similarity Component (100 * similarity_score)
        similarity = pat.get("similarity_score", 0.0)
        # Bounded between 0 and 100
        semantic_score = max(0.0, min(100.0, similarity * 100.0))
        
        # 2. Concept Coverage Component
        concept_score = 0.0
        if keywords:
            title = pat.get("title", "").lower()
            body = pat.get("patent_text", "").lower()
            matches = 0
            for kw in keywords:
                if kw in title or kw in body:
                    matches += 1
            concept_score = (matches / len(keywords)) * 100.0
            
        # 3. Domain Alignment Component
        field_of_inv = pat.get("field_of_invention", "")
        domain_aligned = check_domain_alignment(tech_domain, field_of_inv)
        domain_score = 100.0 if domain_aligned else 0.0
        
        # 4. Metadata Relevance Component (Applicant or IPC match)
        meta_score = 0.0
        applicant = pat.get("applicant_name", "").lower()
        ipc = pat.get("classification_ipc", "").lower()
        
        if hint_applicant and hint_applicant.lower() in applicant:
            meta_score += 50.0
        if hint_ipc and hint_ipc.lower() in ipc:
            meta_score += 50.0
            
        # If no hints were provided, default metadata score to 80% to not penalize
        if not hint_applicant and not hint_ipc:
            meta_score = 80.0
            
        # Calculate final weighted Evidence Score
        evidence_score = (
            (semantic_score * 0.50) +
            (concept_score * 0.20) +
            (domain_score * 0.20) +
            (meta_score * 0.10)
        )
        
        # Add to patent dictionary
        pat_copy = pat.copy()
        pat_copy["evidence_score"] = float(round(evidence_score, 2))
        pat_copy["scoring_breakdown"] = {
            "semantic": float(round(semantic_score, 2)),
            "concept_coverage": float(round(concept_score, 2)),
            "domain_alignment": float(round(domain_score, 2)),
            "metadata_relevance": float(round(meta_score, 2))
        }
        ranked_results.append(pat_copy)
        
    # Sort in descending order of Evidence Score
    ranked_results.sort(key=lambda x: x["evidence_score"], reverse=True)
    return ranked_results
