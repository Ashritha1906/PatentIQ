import os
import sys
import time
import argparse
import shutil
import pandas as pd
import numpy as np

# Try to import psutil for memory tracking
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
                return counters.WorkingSetSize / (1024 * 1024)  # MB
        except Exception:
            pass
        return 0.0

def main():
    parser = argparse.ArgumentParser(description="PatentIQ - Full Embedding Generation Pipeline")
    parser.add_argument("--batch-size", type=int, default=512, help="Internal encoding batch size")
    parser.add_argument("--chunk-size", type=int, default=10000, help="Checkpoint chunk size")
    parser.add_argument("--device", type=str, default=None, help="Force PyTorch device (cuda or cpu)")
    args = parser.parse_args()

    print("==================================================")
    print("PatentIQ - Running Full Embedding Generation")
    print(f"Configuration: Batch Size={args.batch_size}, Chunk Size={args.chunk_size}")
    print("==================================================")

    csv_path = os.path.join("data", "processed", "patent_text_dataset.csv")
    output_dir = os.path.join("data", "processed")
    checkpoint_dir = os.path.join(output_dir, "checkpoints")
    
    if not os.path.exists(csv_path):
        print(f"[ERROR] Clean text dataset not found: {csv_path}")
        print("Please run backend/embeddings/build_patent_text.py first.")
        sys.exit(1)

    # Load dataset
    print(f"Loading text dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    total_records = len(df)
    print(f"Loaded {total_records} records.")

    # Check for empty patent_text
    null_texts = df['patent_text'].isna()
    if null_texts.any():
        print(f"[WARNING] Found {null_texts.sum()} null texts, replacing with defaults.")
        df.loc[null_texts, 'patent_text'] = "Unknown Patent"

    texts = df['patent_text'].tolist()

    # Load model
    print("Loading Sentence Transformers model: all-MiniLM-L6-v2...")
    mem_before_model = get_memory_usage()
    start_model_load = time.time()
    
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("[ERROR] sentence-transformers library is not installed.")
        sys.exit(1)

    try:
        # Determine device
        import torch
        device = args.device
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device.upper()}")
        
        model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        sys.exit(1)

    model_load_time = time.time() - start_model_load
    mem_after_model = get_memory_usage()
    print(f"Model loaded in {model_load_time:.2f} seconds.")
    print(f"Model Memory Footprint: {mem_after_model - mem_before_model:.2f} MB (Total Process RAM: {mem_after_model:.2f} MB)")

    # Establish checkpoint dir
    os.makedirs(checkpoint_dir, exist_ok=True)

    # Process in chunks
    num_chunks = int(np.ceil(total_records / args.chunk_size))
    print(f"\nProcessing {total_records} records across {num_chunks} chunks of size {args.chunk_size}...")
    
    start_total_generation = time.time()
    embeddings_dim = 384
    
    for chunk_idx in range(num_chunks):
        start_idx = chunk_idx * args.chunk_size
        end_idx = min(start_idx + args.chunk_size, total_records)
        
        chunk_npy = os.path.join(checkpoint_dir, f"chunk_{start_idx}_{end_idx}.npy")
        chunk_meta = os.path.join(checkpoint_dir, f"chunk_{start_idx}_{end_idx}_meta.csv")
        
        # Check if chunk already exists (Resume capability)
        if os.path.exists(chunk_npy) and os.path.exists(chunk_meta):
            print(f"  [RESUME] Chunk {chunk_idx + 1}/{num_chunks} ({start_idx} to {end_idx}) already exists. Skipping.")
            continue
            
        print(f"  [RUNNING] Chunk {chunk_idx + 1}/{num_chunks} ({start_idx} to {end_idx})...")
        chunk_texts = texts[start_idx:end_idx]
        
        start_chunk_time = time.time()
        mem_before_chunk = get_memory_usage()
        
        # Generate embeddings
        try:
            chunk_embeddings = model.encode(
                chunk_texts,
                batch_size=args.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
        except Exception as e:
            print(f"\n[ERROR] Embedding generation failed at chunk {chunk_idx + 1} ({start_idx} to {end_idx}): {e}")
            print("To resume later, simply run the script again. Pre-existing chunks will not be recomputed.")
            sys.exit(1)
            
        chunk_time = time.time() - start_chunk_time
        mem_after_chunk = get_memory_usage()
        speed = len(chunk_texts) / chunk_time
        
        print(f"    Completed in {chunk_time:.2f}s ({speed:.2f} records/sec). RAM Change: {mem_after_chunk - mem_before_chunk:.2f} MB")
        
        # Save chunk files
        np.save(chunk_npy, chunk_embeddings)
        # Save mapping metadata for this chunk
        chunk_df = df.iloc[start_idx:end_idx].copy()
        chunk_df['embedding_index'] = np.arange(start_idx, end_idx)
        chunk_df[['embedding_index', 'application_number']].to_csv(chunk_meta, index=False)

    total_gen_time = time.time() - start_total_generation
    print(f"\nAll chunks processed in {total_gen_time / 60:.2f} minutes.")
    
    # Concatenate all chunks
    print("\nConsolidating all checkpoints into final files...")
    final_embeddings = np.zeros((total_records, embeddings_dim), dtype=np.float32)
    meta_dfs = []
    
    for chunk_idx in range(num_chunks):
        start_idx = chunk_idx * args.chunk_size
        end_idx = min(start_idx + args.chunk_size, total_records)
        
        chunk_npy = os.path.join(checkpoint_dir, f"chunk_{start_idx}_{end_idx}.npy")
        chunk_meta = os.path.join(checkpoint_dir, f"chunk_{start_idx}_{end_idx}_meta.csv")
        
        # Load and fill pre-allocated numpy array
        chunk_embeddings = np.load(chunk_npy)
        final_embeddings[start_idx:end_idx] = chunk_embeddings
        
        # Load metadata
        meta_df = pd.read_csv(chunk_meta)
        meta_dfs.append(meta_df)

    # Save final embeddings
    final_embeddings_path = os.path.join(output_dir, "patent_embeddings.npy")
    print(f"Saving final embeddings array to: {final_embeddings_path}")
    np.save(final_embeddings_path, final_embeddings)

    # Save final metadata
    final_metadata = pd.concat(meta_dfs, ignore_index=True)
    final_metadata_path = os.path.join(output_dir, "embedding_metadata.csv")
    print(f"Saving final index metadata map to: {final_metadata_path}")
    final_metadata.to_csv(final_metadata_path, index=False)

    # Clean up checkpoint directory
    print("Cleaning up intermediate checkpoints...")
    try:
        shutil.rmtree(checkpoint_dir)
        print("Checkpoints cleared successfully.")
    except Exception as e:
        print(f"[WARNING] Failed to delete checkpoint directory: {e}")

    # File size info
    embeddings_size_mb = os.path.getsize(final_embeddings_path) / (1024 * 1024)
    metadata_size_mb = os.path.getsize(final_metadata_path) / (1024 * 1024)
    
    print("\n==================================================")
    print("Embedding Generation Performance Summary:")
    print("==================================================")
    print(f"Total Records Processed   : {total_records}")
    print(f"Model Load Time           : {model_load_time:.2f} seconds")
    print(f"Total Encoding Runtime    : {total_gen_time:.2f} seconds ({total_gen_time / 60:.2f} minutes)")
    print(f"Average Generation Speed  : {total_records / total_gen_time:.2f} records/sec")
    print(f"Embedding Dimensions      : {embeddings_dim}")
    print(f"Embedding Storage size    : {embeddings_size_mb:.2f} MB")
    print(f"Metadata Storage size     : {metadata_size_mb:.2f} MB")
    print(f"Final Total Memory (RAM)  : {get_memory_usage():.2f} MB")
    print("==================================================")

if __name__ == '__main__':
    main()
