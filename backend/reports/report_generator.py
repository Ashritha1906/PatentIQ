import logging
from backend.rag.retrieve_context import retrieve_patent_context
from backend.rag.context_compressor import compress_context
from backend.rag.context_summarizer import summarize_context
from backend.rag.evidence_ranker import rank_evidence
from backend.intelligence.concept_clustering import generate_concept_map_and_landscape
from backend.intelligence.novelty_scoring import calculate_novelty_score
from backend.intelligence.innovation_gap import detect_innovation_gaps
from backend.llm.patent_analysis import analyze_invention_novelty
from backend.reports.explainability import generate_explainability_traces

logger = logging.getLogger("ReportGenerator")

def calculate_confidence_assessment(ranked_patents, novelty_data):
    """
    Computes a programmatic confidence assessment based on retrieved evidence alignment.
    """
    if not ranked_patents:
        return {
            "rating": "LOW",
            "score": 0.0,
            "explanation": "No matching patents were retrieved. Analysis is unsupported by vector database evidence."
        }
        
    avg_similarity = sum(p["similarity_score"] for p in ranked_patents) / len(ranked_patents)
    avg_evidence = sum(p["evidence_score"] for p in ranked_patents) / len(ranked_patents)
    
    # Calculate score out of 100 with normalized similarity score contribution
    normalized_sim_score = min(1.0, avg_similarity / 0.50) * 60.0
    confidence_score = normalized_sim_score + (avg_evidence * 0.40)
    confidence_score = max(0.0, min(100.0, confidence_score))
    
    if confidence_score >= 75.0:
        rating = "HIGH"
        desc = "The retrieved evidence is highly relevant, showing strong semantic and domain alignment with the user's idea."
    elif confidence_score >= 50.0:
        rating = "MEDIUM"
        desc = "The retrieved evidence has moderate relevance, containing some semantic overlaps but showing slight domain variation."
    else:
        rating = "LOW"
        desc = "The retrieved evidence has low relevance. The search space has weak alignment, reducing analytical certainty."
        
    explanation = (
        f"Confidence Rating: {rating} ({confidence_score:.1f}%)\n"
        f"Explanation: {desc}\n"
        f"  * Average Similarity : {avg_similarity:.4f}\n"
        f"  * Average Evidence Score: {avg_evidence:.1f}/100"
    )
    
    return {
        "rating": rating,
        "score": float(round(confidence_score, 2)),
        "explanation": explanation
    }

def generate_patent_intelligence_report(user_idea, top_k=5, db_path="data/vectordb"):
    """
    Orchestrates the upgraded PatentIQ Phase 4.5 Intelligence Pipeline.
    Retrieves, summarizes, ranks, clusters, scores novelty, detects gaps, and compiles the report.
    """
    logger.info("Starting PatentIQ Intelligence Pipeline run (Phase 4.5)...")
    
    # 1. Retrieve ranked context package
    context_package = retrieve_patent_context(user_idea, top_k=top_k, db_path=db_path)
    retrieved_patents = context_package["retrieved_patents"]
    query_understanding = context_package["query_understanding"]
    
    if not retrieved_patents:
        return "ERROR: No matching patents found in vector database. Ingestion verify required."

    # 2. Compress context for prompt budget
    compression_res = compress_context(retrieved_patents)
    compressed_block = compression_res["compressed_block"]

    # 3. Concept Summarization (Phase 4.5A)
    summary_data = summarize_context(retrieved_patents)

    # 4. Evidence Ranking (Phase 4.5B)
    ranked_patents = rank_evidence(retrieved_patents, query_understanding)

    # 5. Concept Clustering (Phase 4.5C)
    clustering_data = generate_concept_map_and_landscape(retrieved_patents, db_path=db_path)

    # 6. Novelty Scoring (Phase 4.5D)
    novelty_data = calculate_novelty_score(retrieved_patents, query_understanding)

    # 7. Innovation Gap Detection (Phase 4.5E)
    gap_data = detect_innovation_gaps(retrieved_patents, query_understanding)

    # 8. AI Analysis (Phase 4)
    gemini_analysis = analyze_invention_novelty(user_idea, compressed_block)

    # 9. Explainability Traces (Phase 3)
    explainability_traces = generate_explainability_traces(retrieved_patents, query_understanding)

    # 10. Confidence Assessment (Phase 4.5F)
    confidence_data = calculate_confidence_assessment(ranked_patents, novelty_data)

    # Compile report structure keeping FACTS and INTERPRETATIONS separated
    report = []
    report.append("==================================================")
    report.append("PATENTIQ PATENT INTELLIGENCE REPORT")
    report.append("==================================================\n")
    
    report.append("--- USER INVENTION IDEA ---")
    report.append(f"Idea: {user_idea}\n")
    
    report.append("--- TECHNOLOGY DOMAIN ---")
    report.append(f"Primary Domain: {query_understanding.get('technology_domain', 'GENERAL ENGINEERING')}")
    report.append(f"Key Concepts  : {', '.join(query_understanding.get('key_concepts', []))}\n")
    
    # FACTS SECTION
    report.append("==================================================")
    report.append("PART I: RETRIEVED EVIDENCE (FACTS)")
    report.append("==================================================")
    report.append("The following data is extracted directly from the index database:\n")
    
    for idx, pat in enumerate(ranked_patents):
        app_num = pat["application_number"]
        report.append(f"[{idx + 1}] Patent ID : {app_num}")
        report.append(f"    Title     : {pat['title']}")
        report.append(f"    Applicant : {pat['applicant_name']}")
        report.append(f"    Field     : {pat['field_of_invention']} | IPC: {pat['classification_ipc']}")
        report.append("--------------------------------------------------")
    report.append("")
    
    report.append("==================================================")
    report.append("PART II: EVIDENCE RANKING & CONCEPTS (FACTS)")
    report.append("==================================================")
    report.append("Programmatic assessment of metadata relevance and similarities:\n")
    for idx, pat in enumerate(ranked_patents):
        app_num = pat["application_number"]
        bd = pat["scoring_breakdown"]
        report.append(f"Patent ID: {app_num}")
        report.append(f"  Overall Evidence Score: {pat['evidence_score']:.1f} / 100")
        report.append(f"  Breakdown: Semantic={bd['semantic']:.1f} | Concept={bd['concept_coverage']:.1f} | Domain={bd['domain_alignment']:.1f} | Meta={bd['metadata_relevance']:.1f}")
        report.append("--------------------------------------------------")
    report.append("")
    
    report.append("==================================================")
    report.append("PART III: CONCEPT CLUSTERING (FACTS)")
    report.append("==================================================")
    report.append(clustering_data["concept_map"])
    report.append("\n" + clustering_data["cluster_summary"])
    report.append("")
    
    report.append("==================================================")
    report.append("PART IV: SHARED & UNIQUE CONCEPTS (FACTS)")
    report.append("==================================================")
    report.append(f"Shared Concepts:\n  * " + "\n  * ".join(summary_data.get("shared_concepts", [])))
    report.append(f"\nUnique Concepts:\n  * " + "\n  * ".join(summary_data.get("unique_concepts", [])))
    report.append(f"\nDomains Involved: {', '.join(summary_data.get('domains', []))}")
    report.append(f"Thematic Themes : {', '.join(summary_data.get('themes', []))}\n")
    
    report.append("==================================================")
    report.append("PART V: SEARCH EXPLAINABILITY TRACES (FACTS)")
    report.append("==================================================")
    for idx, pat in enumerate(retrieved_patents):
        app_num = pat["application_number"]
        trace = explainability_traces[app_num]
        report.append(f"Patent ID: {app_num} ({trace['title'][:50]}...)")
        report.append(f"  Similarity Score: {trace['similarity_score']:.4f}")
        report.append(f"  Matched Concepts: {', '.join(trace['matched_concepts']) if trace['matched_concepts'] else 'None'}")
        report.append(f"  Domain Alignment: {trace['technology_alignment']}")
        report.append(f"  Reason: {trace['reason_retrieved']}")
        report.append("--------------------------------------------------")
    report.append("")

    # AI INTERPRETATION SECTION
    report.append("==================================================")
    report.append("PART VI: AI NOVELTY SCORING (INTERPRETATION)")
    report.append("==================================================")
    report.append(f"Novelty Score estimation: {novelty_data['novelty_score']} / 100")
    report.append(f"Novelty Classification  : {novelty_data['band']}")
    report.append(f"\nNovelty Analysis Detail:\n{novelty_data['explanation']}\n")
    
    report.append("==================================================")
    report.append("PART VII: POTENTIAL INNOVATION GAPS (INTERPRETATION)")
    report.append("==================================================")
    report.append("Identified white-space and weakly represented areas:\n")
    for idx, gap in enumerate(gap_data):
        report.append(f"[{idx + 1}] Concept: {gap['concept']}")
        report.append(f"    Status : {gap['representation_status']}")
        report.append(f"    Detail : {gap['explanation']}")
        report.append("--------------------------------------------------")
    report.append("")
    
    report.append("==================================================")
    report.append("PART VIII: AI REASONING & COMPARATIVE NOVELTY (INTERPRETATION)")
    report.append("==================================================")
    report.append(gemini_analysis)
    report.append("")
    
    report.append("==================================================")
    report.append("PART IX: CONFIDENCE & EVIDENCE QUALITY ASSESSMENT")
    report.append("==================================================")
    report.append(confidence_data["explanation"])
    report.append("\n==================================================")
    
    final_report_text = "\n".join(report)
    
    return {
        "report_text": final_report_text,
        "retrieved_patents": retrieved_patents,
        "query_understanding": query_understanding,
        "explainability_traces": explainability_traces,
        "gemini_analysis": gemini_analysis,
        "novelty_data": novelty_data,
        "gap_data": gap_data,
        "ranked_patents": ranked_patents,
        "clustering_data": clustering_data,
        "summary_data": summary_data,
        "confidence_data": confidence_data
    }
