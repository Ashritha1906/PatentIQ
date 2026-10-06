# Phase 6A Retrieval Evaluation: Baseline Semantic Search vs. Phase 6A NL Hybrid Retrieval
import os
import sys
import time
import json
import logging
import numpy as np

# Ensure backend is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.retrieval.search_patents import get_retrieval_resources, semantic_search
from backend.llm.query_understanding import plan_patent_query
from backend.retrieval.nl_retrieval import execute_nl_hybrid_search

logging.basicConfig(level=logging.WARNING)

BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Find patents related to AI-based detection of diabetic retinopathy using retinal images.",
        "domain": "Biomedical / AI",
        "key_concepts": ["retinopathy", "retinal", "image", "detection", "diabetic", "eye"]
    },
    {
        "id": 2,
        "query": "Deep neural network architectures for real-time dermoscopic skin lesion image classification.",
        "domain": "Healthcare / AI",
        "key_concepts": ["skin", "lesion", "dermoscopic", "classification", "neural", "image"]
    },
    {
        "id": 3,
        "query": "Lithium metal battery with solid-state ceramic electrolyte for high energy density storage.",
        "domain": "Energy Storage",
        "key_concepts": ["battery", "electrolyte", "lithium", "solid-state", "storage", "energy"]
    },
    {
        "id": 4,
        "query": "Millimeter-wave beamforming phased array antenna system for 5G wireless base stations.",
        "domain": "Telecommunications",
        "key_concepts": ["antenna", "beamforming", "5g", "phased array", "wireless", "millimeter"]
    },
    {
        "id": 5,
        "query": "Autonomous vehicle obstacle avoidance using LiDAR point cloud neural network segmentation.",
        "domain": "Autonomous Vehicles",
        "key_concepts": ["lidar", "point cloud", "obstacle", "vehicle", "autonomous", "segmentation"]
    },
    {
        "id": 6,
        "query": "Transformer language models for automated summarization of legal contracts.",
        "domain": "Natural Language Processing",
        "key_concepts": ["transformer", "language", "summarization", "legal", "document", "text"]
    },
    {
        "id": 7,
        "query": "Robotic surgical arm with tactile force feedback control for laparoscopic procedures.",
        "domain": "Robotics",
        "key_concepts": ["robotic", "surgical", "force", "tactile", "feedback", "laparoscopic"]
    },
    {
        "id": 8,
        "query": "Gate-all-around nanosheet transistor structure for sub-3nm semiconductor node.",
        "domain": "Semiconductors",
        "key_concepts": ["transistor", "nanosheet", "gate-all-around", "semiconductor", "finfet"]
    },
    {
        "id": 9,
        "query": "Non-invasive optical continuous glucose monitoring wearable biosensor device.",
        "domain": "Medical Devices",
        "key_concepts": ["glucose", "sensor", "continuous", "optical", "wearable", "monitoring"]
    },
    {
        "id": 10,
        "query": "Post-quantum lattice-based cryptographic key encapsulation mechanism for secure communications.",
        "domain": "Cybersecurity",
        "key_concepts": ["cryptographic", "lattice", "encryption", "key", "quantum", "security"]
    },
    {
        "id": 11,
        "query": "Lipid nanoparticle delivery system for mRNA vaccine therapeutic formulations.",
        "domain": "Biotechnology",
        "key_concepts": ["lipid", "nanoparticle", "mrna", "delivery", "vaccine", "therapeutic"]
    },
    {
        "id": 12,
        "query": "Blockchain consensus protocol for scalable decentralized transaction validation.",
        "domain": "Distributed Systems",
        "key_concepts": ["blockchain", "consensus", "transaction", "decentralized", "ledger"]
    },
    {
        "id": 13,
        "query": "Drone collision avoidance system using monocular optical flow visual odometry.",
        "domain": "Aerospace",
        "key_concepts": ["drone", "collision", "optical flow", "uav", "flight", "avoidance"]
    },
    {
        "id": 14,
        "query": "High efficiency silicon-perovskite tandem solar cell photovoltaic device.",
        "domain": "Solar Energy",
        "key_concepts": ["solar", "perovskite", "photovoltaic", "tandem", "cell", "silicon"]
    },
    {
        "id": 15,
        "query": "Reinforcement learning algorithms for dynamic robotic bipedal walking balance control.",
        "domain": "Robotics / AI",
        "key_concepts": ["reinforcement learning", "robot", "bipedal", "walking", "balance", "control"]
    },
    {
        "id": 16,
        "query": "Carbon capture membrane separation system for industrial flue gas emissions.",
        "domain": "Environmental Engineering",
        "key_concepts": ["carbon", "capture", "membrane", "flue gas", "emission", "separation"]
    },
    {
        "id": 17,
        "query": "Class-D audio power amplifier with pulse width modulation and low harmonic distortion.",
        "domain": "Audio Electronics",
        "key_concepts": ["amplifier", "class-d", "pwm", "distortion", "audio", "power"]
    },
    {
        "id": 18,
        "query": "Computer vision inspection system for automated surface defect detection in steel manufacturing.",
        "domain": "Industrial Vision",
        "key_concepts": ["defect", "inspection", "vision", "surface", "steel", "manufacturing"]
    },
    {
        "id": 19,
        "query": "Water filtration membrane with graphene oxide nanostructures for desalination.",
        "domain": "Materials Science",
        "key_concepts": ["membrane", "graphene", "filtration", "water", "desalination"]
    },
    {
        "id": 20,
        "query": "Low power Bluetooth mesh network routing protocol for smart building IoT sensors.",
        "domain": "IoT Networking",
        "key_concepts": ["bluetooth", "mesh", "network", "iot", "sensor", "routing"]
    },
    {
        "id": 21,
        "query": "Cryogenic cooling system for superconducting magnetic resonance imaging magnets.",
        "domain": "Cryogenics",
        "key_concepts": ["cryogenic", "cooling", "superconducting", "mri", "magnet"]
    },
    {
        "id": 22,
        "query": "Electrochemical catalyst for green hydrogen generation via water electrolysis.",
        "domain": "Hydrogen Energy",
        "key_concepts": ["catalyst", "hydrogen", "electrolysis", "water", "electrochemical"]
    },
    {
        "id": 23,
        "query": "Ultra-fast charging circuit architecture with thermal protection for electric vehicles.",
        "domain": "Automotive Electronics",
        "key_concepts": ["charging", "electric vehicle", "battery", "circuit", "thermal"]
    },
    {
        "id": 24,
        "query": "Self-healing polymeric coating material for anti-corrosion protection of metal pipelines.",
        "domain": "Polymer Materials",
        "key_concepts": ["coating", "self-healing", "polymer", "corrosion", "pipeline"]
    },
    {
        "id": 25,
        "query": "Graph neural network for molecular drug property prediction and virtual screening.",
        "domain": "Cheminformatics",
        "key_concepts": ["graph neural network", "molecular", "drug", "screening", "prediction"]
    }
]

def evaluate_relevance(patent_title, patent_abstract, key_concepts):
    text = (str(patent_title) + " " + str(patent_abstract)).lower()
    matches = sum(1 for c in key_concepts if c.lower() in text)
    return matches >= 1

def run_evaluation():
    print("========================================================================")
    print(" PatentIQ Phase 6A: Retrieval Evaluation & Comparison Benchmark ")
    print(" Evaluating 25 Representative Natural-Language Patent Queries ")
    print("========================================================================")

    collection, model = get_retrieval_resources()

    baseline_p5_list = []
    baseline_mrr_list = []
    baseline_latency_list = []

    nl_p5_list = []
    nl_mrr_list = []
    nl_plan_lat_list = []
    nl_ret_lat_list = []
    nl_total_lat_list = []

    results_table = []

    for bq in BENCHMARK_QUERIES:
        qid = bq["id"]
        query = bq["query"]
        concepts = bq["key_concepts"]

        # --- Baseline: Raw Semantic Search ---
        t0 = time.time()
        base_results = semantic_search(query, top_k=20)
        base_lat = (time.time() - t0) * 1000.0
        baseline_latency_list.append(base_lat)

        base_top5 = base_results[:5] if base_results else []
        base_hits = [1 if evaluate_relevance(r.get("title", ""), r.get("abstract", ""), concepts) else 0 for r in base_top5]
        base_p5 = (sum(base_hits) / 5.0) if base_top5 else 0.0
        baseline_p5_list.append(base_p5)

        base_rr = 0.0
        for rank, hit in enumerate(base_hits, 1):
            if hit == 1:
                base_rr = 1.0 / rank
                break
        baseline_mrr_list.append(base_rr)

        # --- Phase 6A: NL Hybrid Retrieval ---
        t_plan_start = time.time()
        planned_query = plan_patent_query(query)
        plan_lat = (time.time() - t_plan_start) * 1000.0
        nl_plan_lat_list.append(plan_lat)

        t_ret_start = time.time()
        nl_resp = execute_nl_hybrid_search(planned_query, candidate_k=50, top_k=20)
        ret_lat = (time.time() - t_ret_start) * 1000.0
        nl_ret_lat_list.append(ret_lat)
        nl_total_lat_list.append(plan_lat + ret_lat)

        nl_top5 = nl_resp.results[:5] if nl_resp.results else []
        nl_hits = [1 if evaluate_relevance(r.title, r.abstract, concepts) else 0 for r in nl_top5]
        nl_p5 = (sum(nl_hits) / 5.0) if nl_top5 else 0.0
        nl_p5_list.append(nl_p5)

        nl_rr = 0.0
        for rank, hit in enumerate(nl_hits, 1):
            if hit == 1:
                nl_rr = 1.0 / rank
                break
        nl_mrr_list.append(nl_rr)

        results_table.append({
            "id": qid,
            "domain": bq["domain"],
            "base_p5": base_p5,
            "nl_p5": nl_p5,
            "base_mrr": base_rr,
            "nl_mrr": nl_rr,
            "base_lat_ms": round(base_lat, 1),
            "nl_total_ms": round(plan_lat + ret_lat, 1)
        })
        print(f"Query {qid:2d}/25 | {bq['domain'][:18]:18s} | Base P@5: {base_p5:.2f} -> NL P@5: {nl_p5:.2f} | Base Lat: {base_lat:.0f}ms -> NL Lat: {plan_lat+ret_lat:.0f}ms")

    # Summary
    avg_base_p5 = np.mean(baseline_p5_list)
    avg_nl_p5 = np.mean(nl_p5_list)
    avg_base_mrr = np.mean(baseline_mrr_list)
    avg_nl_mrr = np.mean(nl_mrr_list)

    avg_base_lat = np.mean(baseline_latency_list)
    avg_plan_lat = np.mean(nl_plan_lat_list)
    avg_ret_lat = np.mean(nl_ret_lat_list)
    avg_nl_total_lat = np.mean(nl_total_lat_list)

    p5_gain = ((avg_nl_p5 - avg_base_p5) / avg_base_p5 * 100) if avg_base_p5 > 0 else 0
    mrr_gain = ((avg_nl_mrr - avg_base_mrr) / avg_base_mrr * 100) if avg_base_mrr > 0 else 0

    print("\n========================================================================")
    print("                      PHASE 6A BENCHMARK SUMMARY                       ")
    print("========================================================================")
    print(f"Metric                  | Baseline (Raw Semantic) | Phase 6A (NL Hybrid) | Change")
    print(f"------------------------+-------------------------+----------------------+---------")
    print(f"Precision@5             | {avg_base_p5:.3f}                   | {avg_nl_p5:.3f}                | +{p5_gain:.1f}%")
    print(f"Mean Reciprocal Rank    | {avg_base_mrr:.3f}                   | {avg_nl_mrr:.3f}                | +{mrr_gain:.1f}%")
    print(f"Planning Latency (ms)   | N/A                     | {avg_plan_lat:.1f}                | -")
    print(f"Retrieval Latency (ms)  | {avg_base_lat:.1f}                   | {avg_ret_lat:.1f}                | -")
    print(f"Total Search Latency(ms)| {avg_base_lat:.1f}                   | {avg_nl_total_lat:.1f}                | +{avg_nl_total_lat-avg_base_lat:.1f}ms")
    print("========================================================================")

    # Save to JSON report
    report = {
        "total_queries": len(BENCHMARK_QUERIES),
        "metrics": {
            "baseline_precision_at_5": round(float(avg_base_p5), 4),
            "nl_hybrid_precision_at_5": round(float(avg_nl_p5), 4),
            "precision_at_5_improvement_pct": round(float(p5_gain), 2),
            "baseline_mrr": round(float(avg_base_mrr), 4),
            "nl_hybrid_mrr": round(float(avg_nl_mrr), 4),
            "mrr_improvement_pct": round(float(mrr_gain), 2),
            "planning_latency_ms": round(float(avg_plan_lat), 2),
            "retrieval_latency_ms": round(float(avg_ret_lat), 2),
            "total_latency_ms": round(float(avg_nl_total_lat), 2)
        },
        "per_query_results": results_table
    }
    os.makedirs("docs/evaluation", exist_ok=True)
    with open("docs/evaluation/phase6a_benchmark_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("Report saved to docs/evaluation/phase6a_benchmark_report.json")

if __name__ == "__main__":
    run_evaluation()
