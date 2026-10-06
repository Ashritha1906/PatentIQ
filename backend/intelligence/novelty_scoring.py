import logging

logger = logging.getLogger("NoveltyScoring")

NOVELTY_DISCLAIMER = (
    "This is an automated prior-art similarity indicator and is not a legal determination of patentability or novelty."
)

def get_novelty_interpretation(score: int):
    """
    Returns the classification band and standard interpretation text for a given score.
    """
    if score <= 20:
        return "Highly Similar to Existing Patents", (
            "The proposed invention idea exhibits high conceptual and technical overlap with existing patents. "
            "The core problem-solving mechanism, operational steps, and primary components are well-documented "
            "in the retrieved literature. Significant design modifications are required to establish differentiation."
        )
    elif score <= 40:
        return "Moderate Overlap", (
            "The invention idea shares key operational characteristics or component configurations with current patents. "
            "While specific secondary functions or implementation environments may differ, the baseline system "
            "architecture has substantial overlap, suggesting moderate novelty."
        )
    elif score <= 60:
        return "Some Distinguishing Features", (
            "The invention idea demonstrates unique features or specialized optimizations not explicitly detailed "
            "in the retrieved prior art. Although the general domain and foundational concepts are saturated, "
            "the specific configuration or method workflow represents a distinguishing technical deviation."
        )
    elif score <= 80:
        return "Potentially Distinct", (
            "The invention idea proposes a novel combination of technical elements or a new application of concepts "
            "that is not strongly represented in the active patent database. The core methodology exhibits "
            "a high degree of uniqueness, indicating strong potential for differentiation."
        )
    else:
        return "Highly Differentiated", (
            "The proposed invention idea represents a highly differentiated technical approach. It introduces "
            "unique concepts, novel component interactions, or addresses problems in a manner completely unrepresented "
            "in the retrieved patent context. It exhibits minimal overlap with the prior art."
        )

def calculate_novelty_score(retrieved_patents, query_understanding):
    """
    Phase 6A.1: Unified Novelty Indicator.
    
    Calculates a programmatic AI-Estimated Novelty Indicator (0-100) based on:
      - Similarity Overlap (50% weight): Maximum similarity score among retrieved patents.
      - Concept Uniqueness (30% weight): Proportion of user keywords absent from retrieved patents.
      - Domain Saturation (20% weight): Ratio of retrieved patents matching the technology domain.
      
    Outputs a canonical dictionary containing 'score', 'novelty_score', and 'overall_novelty_score'
    so all frontend components, APIs, and exports use the exact same canonical value.
    """
    if not retrieved_patents:
        return {
            "score": 100,
            "novelty_score": 100,
            "overall_novelty_score": 100,
            "indicator_name": "AI-Estimated Novelty Indicator",
            "band": "Highly Differentiated",
            "disclaimer": NOVELTY_DISCLAIMER,
            "explanation": (
                f"The AI-Estimated Novelty Indicator is 100/100, placing this invention in the 'Highly Differentiated' band. "
                f"No prior art patents were found in the index, suggesting complete differentiation.\n\n"
                f"Disclaimer: {NOVELTY_DISCLAIMER}"
            ),
            "breakdown": {"similarity_overlap": 0.0, "concept_uniqueness": 100.0, "domain_saturation": 0.0}
        }
        
    # 1. Similarity Overlap Component
    max_similarity = max(pat.get("similarity_score", 0.0) for pat in retrieved_patents)
    overlap_penalty = max_similarity * 100.0
    
    # 2. Concept Uniqueness Component
    keywords = [kw.lower() for kw in query_understanding.get("keywords", []) if len(kw) > 2]
    uniqueness_score = 100.0
    if keywords:
        found_keywords = set()
        for pat in retrieved_patents:
            title = pat.get("title", "").lower()
            body = (pat.get("patent_text", "") or pat.get("abstract", "")).lower()
            for kw in keywords:
                if kw in title or kw in body:
                    found_keywords.add(kw)
        concept_overlap_ratio = len(found_keywords) / len(keywords)
        uniqueness_score = (1.0 - concept_overlap_ratio) * 100.0
        
    # 3. Domain Saturation Component
    tech_domain = query_understanding.get("technology_domain", "")
    matching_domains = 0
    from backend.rag.evidence_ranker import check_domain_alignment
    for pat in retrieved_patents:
        if check_domain_alignment(tech_domain, pat.get("field_of_invention", "")):
            matching_domains += 1
    domain_saturation = (matching_domains / len(retrieved_patents)) * 100.0
    
    raw_score = 100.0 - (
        (overlap_penalty * 0.50) +
        ((100.0 - uniqueness_score) * 0.30) +
        (domain_saturation * 0.20)
    )
    
    # Clamp score to [0, 100]
    novelty_score = max(0, min(100, int(round(raw_score))))
    band, default_text = get_novelty_interpretation(novelty_score)
    
    explanation = (
        f"The AI-Estimated Novelty Indicator is {novelty_score}/100, placing this invention in the '{band}' band. "
        f"{default_text}\n\n"
        f"Key Contributing Factors:\n"
        f"  * Semantic Overlap: The closest patent matches with a similarity score of {max_similarity:.4f}.\n"
        f"  * Concept Uniqueness: {uniqueness_score:.1f}% of the user's technical concepts are absent from the retrieved prior art.\n"
        f"  * Domain Saturation: {domain_saturation:.1f}% of retrieved patents lie within the same technical domain.\n\n"
        f"Disclaimer: {NOVELTY_DISCLAIMER}"
    )
    
    return {
        "score": novelty_score,
        "novelty_score": novelty_score,
        "overall_novelty_score": novelty_score,
        "indicator_name": "AI-Estimated Novelty Indicator",
        "band": band,
        "disclaimer": NOVELTY_DISCLAIMER,
        "explanation": explanation,
        "breakdown": {
            "similarity_overlap": float(round(overlap_penalty, 2)),
            "concept_uniqueness": float(round(uniqueness_score, 2)),
            "domain_saturation": float(round(domain_saturation, 2))
        }
    }
