import os
import sys
import time
import random
import pickle
import pandas as pd
import numpy as np

# Try to import psutil for memory monitoring
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def get_memory_usage():
    if HAS_PSUTIL:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024) # MB
    else:
        # Fallback for Windows if psutil is not available
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
                return counters.WorkingSetSize / (1024 * 1024) # MB
        except Exception:
            pass
        return 0.0

def build_patent_text(row):
    title = str(row['title']).strip() if not pd.isna(row['title']) else 'Unknown Title'
    field = str(row['field_of_invention']).strip() if not pd.isna(row['field_of_invention']) else 'Unknown Field'
    ipc = str(row['classification_ipc']).strip() if not pd.isna(row['classification_ipc']) else 'Unknown IPC'
    applicant = str(row['applicant_name']).strip() if not pd.isna(row['applicant_name']) else 'Unknown Applicant'
    
    return f"Title: {title}\nField of Invention: {field}\nIPC Classification: {ipc}\nApplicant: {applicant}"

def main():
    print("==================================================")
    print("PatentIQ - Running Small Batch Embedding Test")
    print("==================================================")
    
    csv_path = os.path.join("data", "processed", "all_patents.csv")
    if not os.path.exists(csv_path):
        print(f"[ERROR] Processed patents file not found: {csv_path}")
        sys.exit(1)
        
    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    total_records = len(df)
    print(f"Successfully loaded {total_records} records.")
    
    # Select 100 random patents
    print("Selecting 100 random patents for the test batch...")
    random.seed(42)
    sample_indices = random.sample(range(total_records), 100)
    sample_df = df.iloc[sample_indices].copy()
    
    # Generate representations
    print("Generating text representations...")
    sample_df['patent_text'] = sample_df.apply(build_patent_text, axis=1)
    
    # Calculate lengths
    lengths = sample_df['patent_text'].str.len()
    print(f"Text lengths: min={lengths.min()}, max={lengths.max()}, mean={lengths.mean():.2f}")
    
    # Load model
    print("Loading Sentence Transformers model: all-MiniLM-L6-v2...")
    mem_before_model = get_memory_usage()
    start_model_load = time.time()
    
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("[ERROR] sentence-transformers library is not installed.")
        print("Please run: pip install sentence-transformers")
        sys.exit(1)
        
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        sys.exit(1)
        
    end_model_load = time.time()
    mem_after_model = get_memory_usage()
    model_load_time = end_model_load - start_model_load
    model_mem_delta = mem_after_model - mem_before_model
    print(f"Model loaded in {model_load_time:.2f} seconds.")
    print(f"Memory used by model: {model_mem_delta:.2f} MB (Current total: {mem_after_model:.2f} MB)")
    
    # Generate embeddings
    texts = sample_df['patent_text'].tolist()
    print("Generating embeddings for 100 patents...")
    
    start_embed = time.time()
    mem_before_embed = get_memory_usage()
    
    try:
        embeddings = model.encode(texts, show_progress_bar=False)
    except Exception as e:
        print(f"[ERROR] Embedding generation failed: {e}")
        sys.exit(1)
        
    end_embed = time.time()
    mem_after_embed = get_memory_usage()
    embed_time = end_embed - start_embed
    embed_mem_delta = mem_after_embed - mem_before_embed
    
    print(f"Generated embeddings in {embed_time:.4f} seconds.")
    print(f"Memory change during embedding: {embed_mem_delta:.2f} MB (Current total: {mem_after_embed:.2f} MB)")
    
    # Verify dimensions
    embedding_dim = embeddings.shape[1]
    print(f"Embeddings shape: {embeddings.shape} (Dimensions: {embedding_dim})")
    
    # Save test embeddings and metadata
    os.makedirs(os.path.join("backend", "embeddings"), exist_ok=True)
    out_path = os.path.join("backend", "embeddings", "test_batch_data.pkl")
    print(f"Saving output to {out_path}...")
    
    output_data = {
        "indices": sample_indices,
        "application_numbers": sample_df['application_number'].tolist(),
        "texts": texts,
        "embeddings": embeddings,
        "runtime_stats": {
            "model_load_time_sec": model_load_time,
            "model_mem_delta_mb": model_mem_delta,
            "embed_time_sec": embed_time,
            "embed_mem_delta_mb": embed_mem_delta,
            "total_mem_mb": mem_after_embed
        }
    }
    
    with open(out_path, 'wb') as f:
        pickle.dump(output_data, f)
        
    print("Test batch execution completed successfully!")
    print("==================================================")

if __name__ == '__main__':
    main()
