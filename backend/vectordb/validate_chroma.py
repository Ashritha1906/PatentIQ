import os
import sys
import numpy as np
import pandas as pd
import chromadb

def main():
    print("==================================================")
    print("PatentIQ - Running ChromaDB Integrity Validation")
    print("==================================================")

    db_path = os.path.join("data", "vectordb")
    report_path = os.path.join("backend", "reports", "chroma_validation_report.txt")
    dataset_path = os.path.join("data", "processed", "patent_text_dataset.csv")

    if not os.path.exists(db_path):
        print(f"[ERROR] ChromaDB storage folder not found: {db_path}")
        sys.exit(1)

    # Load dataset to verify random items
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        total_patents = len(df)
    else:
        df = None
        total_patents = 115625

    print(f"Initializing persistent ChromaDB client from {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    
    # 1. Collection existence
    try:
        collection = client.get_collection("patentiq_patents")
        collection_exists = True
        print("[PASS] Collection 'patentiq_patents' exists.")
    except Exception as e:
        collection_exists = False
        print(f"[FAIL] Collection 'patentiq_patents' does not exist or failed to load: {e}")
        sys.exit(1)

    # 2. Total vectors stored check
    stored_count = collection.count()
    count_ok = (stored_count == total_patents)
    if count_ok:
        print(f"[PASS] Stored vector count matches dataset count: {stored_count}")
    else:
        print(f"[FAIL] Stored vector count ({stored_count}) does not match expected ({total_patents})!")

    # 3. Random retrieval verification and dimension check
    random_ok = True
    dim_ok = True
    metadata_ok = True
    
    if df is not None:
        # Pick 5 random patents
        np.random.seed(42)
        sample_indices = np.random.randint(0, len(df), size=5)
        samples = df.iloc[sample_indices]
        
        print("\nRetrieving sample records from ChromaDB to verify alignment:")
        for idx, row in samples.iterrows():
            app_num = str(row['application_number'])
            expected_title = row['title']
            
            # Fetch by ID
            try:
                res = collection.get(
                    ids=[app_num],
                    include=["metadatas", "documents", "embeddings"]
                )
                
                if not res["ids"] or res["ids"][0] != app_num:
                    print(f"  [FAIL] Failed to retrieve record {app_num} by ID.")
                    random_ok = False
                    continue
                
                # Verify metadata mapping
                meta = res["metadatas"][0]
                retrieved_title = meta.get("title")
                if retrieved_title != expected_title and not (pd.isna(expected_title) and retrieved_title == "Unknown"):
                    print(f"  [FAIL] Metadata mismatch! ID: {app_num} | Expected title: '{expected_title}' | Retrieved: '{retrieved_title}'")
                    metadata_ok = False
                else:
                    print(f"  [PASS] ID: {app_num} | Title matched: '{retrieved_title[:50]}...'")
                
                # Check vector dimensions
                if res["embeddings"] is not None and len(res["embeddings"]) > 0:
                    vector = res["embeddings"][0]
                    dim = len(vector)
                    if dim != 384:
                        print(f"  [FAIL] Vector dimension is {dim} (expected 384).")
                        dim_ok = False
                    # Check for NaNs/Infs in list
                    if np.isnan(vector).any() or np.isinf(vector).any():
                        print(f"  [FAIL] Vector contains NaNs or Infs.")
                        dim_ok = False
                else:
                    print(f"  [WARNING] Embeddings were not returned for record {app_num}.")
                    dim_ok = False
                    
            except Exception as e:
                print(f"  [FAIL] Exception during retrieval of ID {app_num}: {e}")
                random_ok = False

    # Print summary
    overall_passed = collection_exists and count_ok and random_ok and dim_ok and metadata_ok
    print("\n==================================================")
    print("ChromaDB Integrity Check Results:")
    print("==================================================")
    print(f"Collection Existence : {'PASS' if collection_exists else 'FAIL'}")
    print(f"Document Count Match : {'PASS' if count_ok else 'FAIL'} (Count: {stored_count})")
    print(f"Random Retrieval     : {'PASS' if random_ok else 'FAIL'}")
    print(f"Embedding Dimensions : {'PASS' if dim_ok else 'FAIL'}")
    print(f"Metadata Integrity   : {'PASS' if metadata_ok else 'FAIL'}")
    print("==================================================")

    # Save validation report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    print(f"Saving ChromaDB validation report to: {report_path}")
    with open(report_path, "w") as f:
        f.write("==================================================\n")
        f.write("PatentIQ - ChromaDB Validation Report\n")
        f.write("==================================================\n\n")
        f.write(f"Collection Name      : patentiq_patents\n")
        f.write(f"Total Stored Count   : {stored_count}\n")
        f.write(f"Database Path        : {db_path}\n\n")
        f.write("Check Results:\n")
        f.write("--------------------------------------------------\n")
        f.write(f"[Collection Existence] : {'PASS' if collection_exists else 'FAIL'}\n")
        f.write(f"[Document Count Check] : {'PASS' if count_ok else 'FAIL'} (Expected: {total_patents}, Found: {stored_count})\n")
        f.write(f"[Random Retrieval]     : {'PASS' if random_ok else 'FAIL'}\n")
        f.write(f"[Embedding Dimensions] : {'PASS' if dim_ok else 'FAIL'} (Expected: 384)\n")
        f.write(f"[Metadata Integrity]   : {'PASS' if metadata_ok else 'FAIL'}\n")
        f.write("--------------------------------------------------\n")
        f.write(f"Overall Status: {'PASSED' if overall_passed else 'FAILED'}\n")
        f.write("==================================================\n")

    if not overall_passed:
        print("[ERROR] One or more ChromaDB validation checks failed.")
        sys.exit(1)
        
    print("ChromaDB validation complete!")
    print("==================================================")

if __name__ == '__main__':
    main()
