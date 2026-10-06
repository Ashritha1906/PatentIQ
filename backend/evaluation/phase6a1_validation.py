import os
import sys
import time
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.api.services.dependencies import get_patent_service
from backend.intelligence.innovation_gap import score_concept_coverage, detect_innovation_gaps
from backend.intelligence.novelty_scoring import calculate_novelty_score

QUERIES = [
    {
        "id": 1,
        "title": "Diabetic Retinopathy Detection",
        "query": "Find patents related to automated detection and classification of diabetic retinopathy from retinal fundus images using computer vision and deep learning, including convolutional neural networks, image preprocessing, lesion detection, feature extraction, and severity grading.",
        "concepts": ["automated detection", "diabetic retinopathy", "retinal fundus images", "computer vision", "deep learning", "convolutional neural networks", "image preprocessing", "lesion detection", "feature extraction", "severity grading"]
    },
    {
        "id": 2,
        "title": "Forest Wildfire Detection",
        "query": "Find patents related to AI-based forest wildfire detection and early prediction using satellite imagery, remote sensing data, meteorological information, temperature, humidity, wind patterns, vegetation indices, and machine learning models.",
        "concepts": ["forest wildfire detection", "early prediction", "satellite imagery", "remote sensing data", "meteorological information", "vegetation indices", "machine learning models"]
    },
    {
        "id": 3,
        "title": "Autonomous Vehicle Pedestrian Collision Avoidance",
        "query": "Find patents related to autonomous vehicle pedestrian detection and collision avoidance using computer vision, camera and sensor data, deep learning object detection, real-time pedestrian tracking, distance estimation, trajectory prediction, and automated braking.",
        "concepts": ["autonomous vehicle", "pedestrian detection", "collision avoidance", "computer vision", "pedestrian tracking", "distance estimation", "trajectory prediction", "automated braking"]
    },
    {
        "id": 4,
        "title": "LLM Legal Document Analysis",
        "query": "Find patents related to using large language models and natural language processing for automated legal document analysis, including contract understanding, legal clause extraction, document summarization, legal question answering, semantic search, retrieval-augmented generation, and identification of risks or obligations.",
        "concepts": ["large language models", "natural language processing", "legal document analysis", "contract understanding", "legal clause extraction", "document summarization", "retrieval-augmented generation", "risks or obligations"]
    },
    {
        "id": 5,
        "title": "Intelligent Traffic Management",
        "query": "Find patents related to intelligent traffic management systems that use real-time traffic data, GPS or map data, road sensors, cameras, historical traffic patterns, and machine learning to predict congestion, estimate travel conditions, identify traffic incidents, and dynamically recommend optimized or safer routes.",
        "concepts": ["intelligent traffic management", "real-time traffic data", "road sensors", "historical traffic patterns", "predict congestion", "traffic incidents", "recommend optimized routes"]
    }
]

def run_validation():
    print("=" * 80)
    print(" PATENTIQ PHASE 6A.1: REAL QUERY RETRIEVAL & WHITESPACE VALIDATION ")
    print("=" * 80)

    service = get_patent_service()
    output_report = []

    for item in QUERIES:
        qid = item["id"]
        qtitle = item["title"]
        qtext = item["query"]
        concepts = item["concepts"]

        print(f"\n[QUERY {qid}/5] {qtitle}")
        print(f"Text: \"{qtext[:90]}...\"")

        t0 = time.time()
        # Execute natural language search with hybrid retrieval
        nl_resp = service.search_natural_language(
            query=qtext,
            top_k=5,
            include_rag=False
        )
        latency_ms = round((time.time() - t0) * 1000.0, 1)

        patents = nl_resp.results[:5]

        # Convert to dictionary for downstream coverage and novelty
        patent_dicts = [
            {
                "application_number": p.publication_number,
                "publication_number": p.publication_number,
                "title": p.title,
                "abstract": p.abstract or "",
                "patent_text": p.abstract or "",
                "similarity_score": p.semantic_score,
                "final_score": p.final_score,
                "keyword_score": p.keyword_score,
                "field_of_invention": p.classification or "GENERAL"
            }
            for p in patents
        ]

        # 1. Concept Coverage Evaluation
        concept_coverages = []
        for c in concepts:
            c_res = score_concept_coverage(c, patent_dicts)
            concept_coverages.append({
                "concept": c,
                "coverage_score": c_res["coverage_score"],
                "coverage_band": c_res["coverage_band"],
                "exact_phrase": c_res["exact_phrase_present"],
                "semantic_presence": c_res["semantic_concept_present"],
                "equivalents": c_res["matched_equivalents"]
            })

        # 2. Whitespace Gap Detection
        qu = {
            "technical_concepts": concepts,
            "keywords": concepts,
            "technology_domain": patents[0].classification if patents else "GENERAL"
        }
        gaps = detect_innovation_gaps(patent_dicts, qu)

        # 3. Novelty Indicator Calculation
        novelty = calculate_novelty_score(patent_dicts, qu)

        # Print summary for terminal
        print(f"  Latency: {latency_ms} ms")
        print(f"  AI-Estimated Novelty Indicator: {novelty['score']}/100 ({novelty['band']})")
        print("  Top 5 Patents:")
        for rank, p in enumerate(patents, 1):
            print(f"    #{rank} [{p.publication_number}] Hybrid: {p.final_score:.3f} | Semantic: {p.semantic_score:.3f} | KW: {p.keyword_score:.3f}")
            print(f"        Title: {p.title[:75]}")

        print("  Concept Coverage Summary:")
        for cc in concept_coverages:
            status_tag = f"[{cc['coverage_band']}]"
            eq_info = f" -> Eq: {', '.join(cc['equivalents'][:2])}" if cc['equivalents'] else ""
            print(f"    - {cc['concept'][:32]:32s}: {cc['coverage_score']:4.1f}% {status_tag}{eq_info}")

        print(f"  Identified Whitespaces ({len(gaps)}):")
        for g in gaps:
            combo_tag = "[COMBO]" if g.get("is_combination") else "[CONCEPT]"
            print(f"    * {combo_tag} {g['concept'][:35]}: {g.get('coverage_score', 0):.0f}% ({g['representation_status']})")

        output_report.append({
            "id": qid,
            "title": qtitle,
            "query": qtext,
            "latency_ms": latency_ms,
            "novelty_score": novelty["score"],
            "novelty_band": novelty["band"],
            "top_5_patents": [
                {
                    "rank": i+1,
                    "publication_number": p.publication_number,
                    "title": p.title,
                    "hybrid_score": p.final_score,
                    "semantic_score": p.semantic_score,
                    "keyword_score": p.keyword_score,
                    "ranking_reasons": p.ranking_reasons
                }
                for i, p in enumerate(patents)
            ],
            "concept_coverages": concept_coverages,
            "whitespaces": [
                {
                    "concept": g["concept"],
                    "representation_status": g["representation_status"],
                    "coverage_score": g.get("coverage_score"),
                    "is_combination": g.get("is_combination", False),
                    "explanation": g["explanation"]
                }
                for g in gaps
            ]
        })

    os.makedirs("docs/evaluation", exist_ok=True)
    with open("docs/evaluation/phase6a1_query_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(output_report, f, indent=2)

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE: Report saved to docs/evaluation/phase6a1_query_validation_report.json")
    print("=" * 80)

if __name__ == "__main__":
    run_validation()
