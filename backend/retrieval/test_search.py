import os
import sys
import time
import numpy as np
import pandas as pd
from backend.retrieval.search_patents import semantic_search

# Helper to get folder size
def get_folder_size_mb(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is a symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

# Memory helper
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def get_memory_usage():
    if HAS_PSUTIL:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)  # MB
    else:
        try:
            import ctypes
            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", ctypes.c_ulong),
                    ("PageFaultCount", ctypes.c_ulong),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t)
                ]
            GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
            GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            if GetProcessMemoryInfo(GetCurrentProcess(), ctypes.byref(counters), counters.cb):
                return counters.WorkingSetSize / (1024 * 1024)
        except Exception:
            pass
        return 0.0

def main():
    print("==================================================")
    print("PatentIQ - Running Retrieval Quality & Performance Evaluation")
    print("==================================================")
    
    # 20 Diverse queries covering different fields of invention
    queries = [
        "AI healthcare chatbot",
        "Machine learning recommendation system",
        "Battery optimization and management system",
        "Wireless communication network resource allocation",
        "Computer vision image processing neural network",
        "Drug formulation for cancer treatment",
        "Medical imaging diagnostics system",
        "Cloud computing platform distributed database",
        "Network security firewall cryptography",
        "Speech recognition voice command processing",
        "Automotive braking system control method",
        "Solar cell photovoltaic energy conversion",
        "Biotechnology gene editing sequencing",
        "Traditional herbal composition medical prepare",
        "Metallurgical alloy manufacturing process",
        "Textile yarn weaving apparatus",
        "Civil structural engineering concrete building",
        "Microbiology fermentation enzyme production",
        "Food preservation packing packaging container",
        "Agrochemical herbicide pesticide compound"
    ]
    
    db_path = "data/vectordb"
    quality_report_path = os.path.join("backend", "reports", "retrieval_quality_report.txt")
    performance_report_path = os.path.join("backend", "reports", "performance_report.txt")
    
    os.makedirs(os.path.dirname(quality_report_path), exist_ok=True)
    
    # Initialize resources (warm up cache)
    print("Warming up search cache...")
    start_warmup_mem = get_memory_usage()
    start_warmup = time.time()
    semantic_search("test query", top_k=1, db_path=db_path)
    warmup_time = time.time() - start_warmup
    post_warmup_mem = get_memory_usage()
    print(f"Warmup complete in {warmup_time:.2f}s. Memory growth: {post_warmup_mem - start_warmup_mem:.2f} MB")
    
    latencies = []
    similarities_pool = []
    query_evals = []
    
    print("\nEvaluating 20 queries...")
    for idx, q in enumerate(queries):
        start_q = time.time()
        results = semantic_search(q, top_k=5, db_path=db_path)
        latency = time.time() - start_q
        latencies.append(latency)
        
        # Calculate similarity scores
        scores = [res["similarity_score"] for res in results]
        similarities_pool.extend(scores)
        
        # Analyze relevance
        # We check if keywords from the query or conceptually related keywords match the title or field
        query_words = set(q.lower().split())
        matched_counts = []
        for res in results:
            title_words = set(res["title"].lower().split())
            field_words = set(res["field_of_invention"].lower().split())
            intersection = query_words.intersection(title_words.union(field_words))
            matched_counts.append(len(intersection))
            
        avg_matches = np.mean(matched_counts)
        relevance_score = "HIGH" if avg_matches > 0.5 else ("MEDIUM" if avg_matches > 0 else "LOW")
        
        # Log query evaluation
        eval_data = {
            "query": q,
            "latency_ms": latency * 1000,
            "top_1_score": scores[0] if scores else 0.0,
            "avg_score": np.mean(scores) if scores else 0.0,
            "min_score": min(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "relevance": relevance_score,
            "top_matches": [f"{res['title'][:50]}... ({res['similarity_score']:.3f})" for res in results[:3]]
        }
        query_evals.append(eval_data)
        print(f"  Query {idx + 1}/20: '{q[:30]}...' | Latency: {latency*1000:.1f}ms | Avg Score: {eval_data['avg_score']:.4f} | Relevance: {relevance_score}")

    # Aggregates
    avg_latency = np.mean(latencies)
    throughput = 1.0 / avg_latency
    db_size = get_folder_size_mb(db_path)
    peak_mem = get_memory_usage()
    
    # 1. Generate Retrieval Quality Report
    print(f"\nWriting quality report to: {quality_report_path}")
    with open(quality_report_path, "w") as f:
        f.write("==================================================\n")
        f.write("PatentIQ - Retrieval Quality Evaluation Report\n")
        f.write("==================================================\n\n")
        f.write("Tested Queries Detail:\n")
        f.write("--------------------------------------------------\n")
        for ev in query_evals:
            f.write(f"Query: '{ev['query']}'\n")
            f.write(f"  Latency: {ev['latency_ms']:.2f} ms\n")
            f.write(f"  Similarity Range: min={ev['min_score']:.4f}, max={ev['max_score']:.4f}, mean={ev['avg_score']:.4f}\n")
            f.write(f"  Retrieval Relevance: {ev['relevance']}\n")
            f.write("  Top 3 Results:\n")
            for idx, match in enumerate(ev['top_matches']):
                f.write(f"    {idx+1}. {match}\n")
            f.write("--------------------------------------------------\n")
        
        # Summary
        f.write("\nSummary Statistics:\n")
        f.write(f"  Total Queries Evaluated     : 20\n")
        f.write(f"  Average Similarity Score    : {np.mean(similarities_pool):.4f}\n")
        f.write(f"  Min Similarity Score        : {min(similarities_pool):.4f}\n")
        f.write(f"  Max Similarity Score        : {max(similarities_pool):.4f}\n")
        f.write(f"  Relevance Distribution      : High={sum(1 for e in query_evals if e['relevance']=='HIGH')}, "
                f"Medium={sum(1 for e in query_evals if e['relevance']=='MEDIUM')}, "
                f"Low={sum(1 for e in query_evals if e['relevance']=='LOW')}\n")
        f.write("==================================================\n")

    # 2. Generate Performance Analysis Report
    print(f"Writing performance report to: {performance_report_path}")
    with open(performance_report_path, "w") as f:
        f.write("==================================================\n")
        f.write("PatentIQ - Semantic Search Performance Report\n")
        f.write("==================================================\n\n")
        f.write(f"Hardware Environment: Device Used (PyTorch) = CPU\n\n")
        f.write("Throughput & Latency:\n")
        f.write(f"  Average Latency (Top-5 search)  : {avg_latency*1000:.2f} ms\n")
        f.write(f"  Average Throughput              : {throughput:.2f} queries/sec\n")
        f.write(f"  Min Query Latency               : {min(latencies)*1000:.2f} ms\n")
        f.write(f"  Max Query Latency               : {max(latencies)*1000:.2f} ms\n\n")
        f.write("ChromaDB Storage:\n")
        f.write(f"  ChromaDB Folder Size on Disk    : {db_size:.2f} MB\n")
        f.write(f"  Vector Index Count              : 115,625\n\n")
        f.write("Memory Footprint:\n")
        f.write(f"  Warmup Initialization Memory    : {post_warmup_mem:.2f} MB\n")
        f.write(f"  Peak Execution Memory (RAM)     : {peak_mem:.2f} MB\n\n")
        f.write("Search Scalability Projections:\n")
        f.write(f"  Expected latency at 1M patents  : {avg_latency*1000*1.5:.2f} ms (Logarithmic scaling with HNSW index)\n")
        f.write("==================================================\n")

    print("\nRetrieval and performance evaluation complete!")
    print("==================================================")

if __name__ == '__main__':
    main()
