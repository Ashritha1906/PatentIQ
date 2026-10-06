import os
import sys
import numpy as np
import pandas as pd

def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def main():
    print("==================================================")
    print("PatentIQ - Running Embedding Validation")
    print("==================================================")

    embeddings_path = os.path.join("data", "processed", "patent_embeddings.npy")
    metadata_path = os.path.join("data", "processed", "embedding_metadata.csv")
    dataset_path = os.path.join("data", "processed", "patent_text_dataset.csv")
    report_path = os.path.join("data", "processed", "embedding_validation_report.txt")

    # Verify files exist
    for path in [embeddings_path, metadata_path, dataset_path]:
        if not os.path.exists(path):
            print(f"[ERROR] Required file not found: {path}")
            sys.exit(1)

    print("Loading files...")
    embeddings = np.load(embeddings_path)
    metadata = pd.read_csv(metadata_path)
    dataset = pd.read_csv(dataset_path)

    total_embeddings = len(embeddings)
    total_metadata = len(metadata)
    total_dataset = len(dataset)

    print(f"Loaded {total_embeddings} embeddings.")
    print(f"Loaded {total_metadata} metadata records.")
    print(f"Loaded {total_dataset} dataset records.")

    # Validation Checks
    results = {}
    
    # 1. Total count matches
    count_ok = (total_embeddings == total_dataset == total_metadata)
    results["count_check"] = {
        "status": "PASS" if count_ok else "FAIL",
        "message": f"Embeddings: {total_embeddings}, Dataset: {total_dataset}, Metadata: {total_metadata}"
    }

    # 2. Dimensions check
    dim_ok = (embeddings.ndim == 2 and embeddings.shape[1] == 384)
    results["dimension_check"] = {
        "status": "PASS" if dim_ok else "FAIL",
        "message": f"Embeddings shape: {embeddings.shape}"
    }

    # 3. NaN check
    nan_count = np.isnan(embeddings).sum()
    nan_ok = (nan_count == 0)
    results["nan_check"] = {
        "status": "PASS" if nan_ok else "FAIL",
        "message": f"Found {nan_count} NaN values"
    }

    # 4. Infinite check
    inf_count = np.isinf(embeddings).sum()
    inf_ok = (inf_count == 0)
    results["inf_check"] = {
        "status": "PASS" if inf_ok else "FAIL",
        "message": f"Found {inf_count} Infinite values"
    }

    # 5. Vector norms check
    norms = np.linalg.norm(embeddings, axis=1)
    # Norms should be close to 1.0 (within epsilon due to float32 precision)
    norm_tolerance = 1e-4
    invalid_norms = np.abs(norms - 1.0) > norm_tolerance
    invalid_norm_count = invalid_norms.sum()
    norms_ok = (invalid_norm_count == 0)
    results["norms_check"] = {
        "status": "PASS" if norms_ok else "FAIL",
        "message": f"Found {invalid_norm_count} vectors with invalid L2 norms (average norm: {np.mean(norms):.6f})"
    }

    # 6. Random sample similarity check
    similarities = []
    np.random.seed(42)
    sample_size = 50
    for _ in range(sample_size):
        idx1 = np.random.randint(0, total_embeddings)
        idx2 = np.random.randint(0, total_embeddings)
        while idx1 == idx2:
            idx2 = np.random.randint(0, total_embeddings)
        
        sim = cosine_similarity(embeddings[idx1], embeddings[idx2])
        similarities.append(sim)
        
    avg_sim = np.mean(similarities)
    min_sim = min(similarities)
    max_sim = max(similarities)
    results["similarity_check"] = {
        "status": "PASS" if avg_sim < 0.8 else "WARNING",
        "message": f"Cosine similarity over 50 sample pairs: min={min_sim:.4f}, max={max_sim:.4f}, mean={avg_sim:.4f}"
    }

    # Print results
    print("\n==================================================")
    print("Embedding Validation Results:")
    print("==================================================")
    all_passed = True
    for test, res in results.items():
        print(f"[{res['status']}] {test.replace('_', ' ').title()}")
        print(f"      {res['message']}")
        if res["status"] == "FAIL":
            all_passed = False
    print("==================================================")

    # Generate Report File
    print(f"Writing validation report to: {report_path}")
    with open(report_path, "w") as f:
        f.write("==================================================\n")
        f.write("PatentIQ - Embedding Validation Report\n")
        f.write("==================================================\n\n")
        f.write(f"Total Embeddings  : {total_embeddings}\n")
        f.write(f"Metadata Records  : {total_metadata}\n")
        f.write(f"Dataset Records   : {total_dataset}\n\n")
        f.write("Test Execution Summary:\n")
        f.write("--------------------------------------------------\n")
        for test, res in results.items():
            f.write(f"[{res['status']}] {test.replace('_', ' ').title()}\n")
            f.write(f"      {res['message']}\n")
        f.write("--------------------------------------------------\n")
        f.write(f"Overall Status: {'PASSED' if all_passed else 'FAILED'}\n")
        f.write("==================================================\n")

    if not all_passed:
        print("[ERROR] One or more validation checks failed.")
        sys.exit(1)
        
    print("Embedding validation complete!")
    print("==================================================")

if __name__ == '__main__':
    main()
