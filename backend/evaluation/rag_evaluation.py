import os
import re
import sys
import time
import numpy as np
import pandas as pd
import logging
from backend.retrieval.stress_test import INVENTIONS
from backend.reports.report_generator import generate_patent_intelligence_report

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RAGEvaluation")

def extract_application_numbers(text):
    """
    Helper to extract application numbers from generated text using regex.
    Supports patterns like:
      - 1/CHE/2010
      - 2018/MUMNP/2011
      - 7461/CHENP/2010
    """
    if not text:
        return set()
    # Simple alphanumeric patterns with slashes
    pattern1 = re.findall(r'\b\d+/[A-Z]+/\d+\b', text)
    pattern2 = re.findall(r'\b\d+/[A-Z]+NP/\d+\b', text)
    return set(pattern1 + pattern2)

def evaluate_rag_run(user_idea, db_path="data/vectordb"):
    """
    Runs the full RAG pipeline and evaluates metrics on the output.
    """
    start_time = time.time()
    
    # Run pipeline
    res = generate_patent_intelligence_report(user_idea, top_k=5, db_path=db_path)
    if isinstance(res, str) and res.startswith("ERROR"):
        raise ValueError(res)
        
    latency_sec = time.time() - start_time
    
    retrieved = res["retrieved_patents"]
    retrieved_app_nums = set(pat["application_number"] for pat in retrieved)
    
    # 1. Retrieval Quality: Mean cosine similarity of Top-5
    scores = [pat["similarity_score"] for pat in retrieved]
    mean_similarity = np.mean(scores) if scores else 0.0
    
    # 2. Context Quality: Token/Character reduction ratio
    # Characters of raw patent text bodies
    raw_char_count = sum(len(pat.get("patent_text", "")) for pat in retrieved)
    compressed_char_count = len(res["gemini_analysis"]) # Approx size
    compression_ratio = 1.0 - (compressed_char_count / raw_char_count) if raw_char_count > 0 else 0.0

    # 3. Hallucination Risk: Check if generated analysis mentions invalid patent numbers
    analysis_text = res["gemini_analysis"]
    mentioned_app_nums = extract_application_numbers(analysis_text)
    
    # Find any mentioned IDs that were NOT in the retrieved context set
    hallucinated_ids = mentioned_app_nums - retrieved_app_nums
    hallucination_detected = 1 if len(hallucinated_ids) > 0 else 0
    
    # 4. Evidence Usage: % of retrieved patents explicitly cited/mentioned
    cited_count = sum(1 for app_num in retrieved_app_nums if app_num in analysis_text)
    evidence_usage_pct = (cited_count / len(retrieved_app_nums)) * 100 if retrieved_app_nums else 0.0
    
    # 5. Analysis Consistency: Assert that required sections are present
    required_sections = [
        "Similar Technologies",
        "Overlapping Concepts",
        "Technical Similarities",
        "Potential Novel Areas",
        "Innovation Opportunities",
        "Technology Classification"
    ]
    sections_present = sum(1 for section in required_sections if section.lower() in analysis_text.lower())
    consistency_score = (sections_present / len(required_sections)) * 100

    return {
        "latency_sec": latency_sec,
        "mean_similarity": mean_similarity,
        "compression_ratio": compression_ratio,
        "hallucination_detected": hallucination_detected,
        "hallucinated_ids": list(hallucinated_ids),
        "evidence_usage_pct": evidence_usage_pct,
        "consistency_score": consistency_score,
        "report_text": res["report_text"]
    }

def main():
    print("==================================================")
    print("PatentIQ - Running Phase 4 RAG Evaluation")
    print(f"Total Test Inventions to Evaluate: {len(INVENTIONS)}")
    print("==================================================")

    db_path = "data/vectordb"
    report_path = os.path.join("backend", "reports", "rag_evaluation_report.txt")
    sample_report_dir = os.path.join("backend", "reports", "samples")
    os.makedirs(sample_report_dir, exist_ok=True)

    latencies = []
    similarities = []
    compressions = []
    hallucinations = 0
    evidence_usages = []
    consistencies = []
    
    evaluation_logs = []

    # Select a representative subset of 10 inventions (one per category) to respect rate limits
    categories_seen = set()
    test_inventions = []
    for inv in INVENTIONS:
        cat = inv["category"]
        if cat not in categories_seen:
            categories_seen.add(cat)
            test_inventions.append(inv)
            
    if len(test_inventions) < 10:
        test_inventions = INVENTIONS[:10]

    print(f"Filtered to {len(test_inventions)} representative inventions (one per tech category).")

    # Run evaluations with slight delays to respect Gemini API rate limits
    print("\nRunning RAG pipelines and metrics checks...")
    for idx, inv in enumerate(test_inventions):
        inv_id = inv["id"]
        # We test on the Medium (3-sentence) version of each invention for stable balance
        idea = inv["medium"]
        
        logger.info(f"Evaluating {idx+1}/{len(test_inventions)}: {inv_id}...")
        
        try:
            eval_metrics = evaluate_rag_run(idea, db_path=db_path)
        except Exception as e:
            logger.error(f"Failed RAG run for query {inv_id}: {e}")
            continue
            
        latencies.append(eval_metrics["latency_sec"])
        similarities.append(eval_metrics["mean_similarity"])
        compressions.append(eval_metrics["compression_ratio"])
        hallucinations += eval_metrics["hallucination_detected"]
        evidence_usages.append(eval_metrics["evidence_usage_pct"])
        consistencies.append(eval_metrics["consistency_score"])
        
        evaluation_logs.append({
            "id": inv_id,
            "latency_ms": eval_metrics["latency_sec"] * 1000,
            "mean_similarity": eval_metrics["mean_similarity"],
            "compression_ratio": eval_metrics["compression_ratio"],
            "hallucination_detected": eval_metrics["hallucination_detected"],
            "hallucinated_ids": eval_metrics["hallucinated_ids"],
            "evidence_usage_pct": eval_metrics["evidence_usage_pct"],
            "consistency_score": eval_metrics["consistency_score"]
        })
        
        # Save first 3 reports as samples
        if idx < 3:
            sample_path = os.path.join(sample_report_dir, f"sample_report_{inv_id}.txt")
            with open(sample_path, "w", encoding="utf-8") as sf:
                sf.write(eval_metrics["report_text"])
            logger.info(f"Saved sample report to: {sample_path}")
            
        # Small break between loops, rate limiting is handled internally in gemini_client.py
        time.sleep(1)


    # Compute aggregate stats
    total_runs = len(latencies)
    if total_runs == 0:
        print("[ERROR] No successful evaluation runs completed.")
        sys.exit(1)
        
    avg_latency = np.mean(latencies)
    avg_similarity = np.mean(similarities)
    avg_compression = np.mean(compressions)
    hallucination_rate = (hallucinations / total_runs) * 100
    avg_evidence_usage = np.mean(evidence_usages)
    avg_consistency = np.mean(consistencies)

    # Calculate overall RAG score
    # Score metrics
    score_relevance = min(100.0, avg_similarity / 0.60 * 100)
    score_compression = avg_compression * 100
    score_hallucination = 100.0 - hallucination_rate
    score_evidence = avg_evidence_usage
    score_consistency = avg_consistency
    
    rag_score = (
        (score_relevance * 0.25) +
        (score_compression * 0.15) +
        (score_hallucination * 0.30) +
        (score_evidence * 0.20) +
        (score_consistency * 0.10)
    )

    # Output Report File
    print(f"\nSaving final RAG evaluation report to: {report_path}")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write("PatentIQ - Phase 4 RAG Evaluation Report\n")
        f.write("==================================================\n\n")
        f.write(f"Total Successful Runs  : {total_runs} / {len(test_inventions)}\n")
        f.write(f"Overall RAG Score      : {rag_score:.2f} / 100\n")
        f.write(f"RAG System Decision    : {'GO FOR PRODUCTION' if rag_score >= 80 else 'NO-GO'}\n\n")
        
        f.write("Key Performance Metrics Summary:\n")
        f.write("--------------------------------------------------\n")
        f.write(f"  1. Average Latency (End-to-End) : {avg_latency*1000:.2f} ms\n")
        f.write(f"  2. Mean Context Similarity      : {avg_similarity:.4f}\n")
        f.write(f"  3. Context Compression Ratio    : {avg_compression*100:.2f}%\n")
        f.write(f"  4. Hallucination Rate           : {hallucination_rate:.2f}%\n")
        f.write(f"  5. Context Evidence Citation    : {avg_evidence_usage:.2f}%\n")
        f.write(f"  6. Section Consistency Score    : {avg_consistency:.2f}%\n")
        f.write("--------------------------------------------------\n\n")
        
        f.write("Individual Run Metrics Log:\n")
        f.write("--------------------------------------------------\n")
        for log in evaluation_logs:
            f.write(f"ID: {log['id']}\n")
            f.write(f"  Similarity: {log['mean_similarity']:.4f} | Latency: {log['latency_ms']:.1f}ms\n")
            f.write(f"  Compression: {log['compression_ratio']*100:.1f}% | Cite Rate: {log['evidence_usage_pct']:.1f}%\n")
            f.write(f"  Hallucination: {'YES' if log['hallucination_detected'] else 'NO'} (Hallucinated IDs: {log['hallucinated_ids']})\n")
            f.write(f"  Consistency: {log['consistency_score']:.1f}%\n")
            f.write("--------------------------------------------------\n")
            
        f.write("==================================================\n")

    print("\nRAG Evaluation Complete!")
    print(f"Overall RAG Score: {rag_score:.2f} / 100")
    print("==================================================")

if __name__ == '__main__':
    main()
