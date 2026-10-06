import os
import sys
import pickle
import numpy as np

def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def main():
    print("==================================================")
    print("PatentIQ - Validating Test Embeddings")
    print("==================================================")
    
    pkl_path = os.path.join("backend", "embeddings", "test_batch_data.pkl")
    if not os.path.exists(pkl_path):
        print(f"[FAIL] Test embeddings pickle file not found: {pkl_path}")
        print("Please run backend/embeddings/test_embeddings.py first.")
        sys.exit(1)
        
    print(f"Loading data from {pkl_path}...")
    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
    except Exception as e:
        print(f"[FAIL] Failed to load pickle file: {e}")
        sys.exit(1)
        
    # Check structure
    required_keys = ["indices", "application_numbers", "texts", "embeddings", "runtime_stats"]
    for key in required_keys:
        if key not in data:
            print(f"[FAIL] Missing required key in output: {key}")
            sys.exit(1)
    print("[PASS] Output file structure is correct (contains all required keys).")
    
    embeddings = data["embeddings"]
    texts = data["texts"]
    app_nums = data["application_numbers"]
    indices = data["indices"]
    stats = data["runtime_stats"]
    
    # 1. Validate counts
    num_embeddings = len(embeddings)
    if num_embeddings != 100:
        print(f"[FAIL] Expected 100 embeddings, but found {num_embeddings}")
        sys.exit(1)
    print(f"[PASS] Successfully verified embedding count: {num_embeddings}")
    
    # Verify match of lists
    if len(texts) != 100 or len(app_nums) != 100 or len(indices) != 100:
        print(f"[FAIL] Mismatch in array lengths! "
              f"Embeddings: {num_embeddings}, Texts: {len(texts)}, "
              f"AppNums: {len(app_nums)}, Indices: {len(indices)}")
        sys.exit(1)
    print("[PASS] Metadata list lengths match embedding counts.")
    
    # 2. Validate dimensions
    if embeddings.ndim != 2:
        print(f"[FAIL] Embeddings should be a 2D array, but got shape {embeddings.shape}")
        sys.exit(1)
        
    dim = embeddings.shape[1]
    if dim != 384:
        print(f"[FAIL] Expected embedding dimension 384 (all-MiniLM-L6-v2), but got {dim}")
        sys.exit(1)
    print(f"[PASS] Embedding dimensions are correct: {dim}")
    
    # 3. Validate content (no NaNs or Infs)
    if np.isnan(embeddings).any():
        print("[FAIL] Found NaN values in the generated embeddings!")
        sys.exit(1)
    if np.isinf(embeddings).any():
        print("[FAIL] Found Infinite values in the generated embeddings!")
        sys.exit(1)
    print("[PASS] Embeddings checked: No NaNs or Infinite values found.")
    
    # Check normalization
    norms = np.linalg.norm(embeddings, axis=1)
    avg_norm = np.mean(norms)
    print(f"[INFO] Average embedding vector norm: {avg_norm:.4f} (expected close to 1.0 for normalized vectors)")
    
    # Check similarity variance on sample pairs
    similarities = []
    for i in range(10):
        # Pick 2 random embeddings
        idx1 = np.random.randint(0, 100)
        idx2 = np.random.randint(0, 100)
        while idx1 == idx2:
            idx2 = np.random.randint(0, 100)
        sim = cosine_similarity(embeddings[idx1], embeddings[idx2])
        similarities.append(sim)
    
    print(f"[INFO] Cosine similarity sample range: min={min(similarities):.4f}, "
          f"max={max(similarities):.4f}, mean={np.mean(similarities):.4f}")
    
    # 4. Check Runtime & Memory stats
    print("\n==================================================")
    print("Runtime & Memory Statistics (from test batch):")
    print("==================================================")
    print(f"Model Load Time : {stats['model_load_time_sec']:.2f} seconds")
    print(f"Model Memory    : {stats['model_mem_delta_mb']:.2f} MB")
    print(f"Encoding Time   : {stats['embed_time_sec']:.4f} seconds (for 100 patents)")
    print(f"Encoding Memory : {stats['embed_mem_delta_mb']:.2f} MB")
    print(f"Total Memory    : {stats['total_mem_mb']:.2f} MB")
    
    # Project stats for 115,625 records
    total_records = 115625
    projected_time_sec = (stats['embed_time_sec'] / 100) * total_records
    projected_time_min = projected_time_sec / 60
    print(f"Projected Encoding Time (Full Dataset): {projected_time_min:.2f} minutes")
    
    print("--------------------------------------------------")
    print("Status: ALL VALIDATION TESTS PASSED!")
    print("==================================================")

if __name__ == '__main__':
    main()
