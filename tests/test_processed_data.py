#!/usr/bin/env python3
"""
PatentIQ - Phase 1: Preprocessed Data Validation Script
This script verifies the integrity and quality of all_patents.csv.

Author: Antigravity AI Mentor
"""

import os
import re
import sys
import pandas as pd

def run_validation():
    print("==================================================")
    print("Starting Post-Preprocessing Validation Tests...")
    print("==================================================")
    
    file_path = os.path.join("data", "processed", "all_patents.csv")
    
    # 1. Check file existence
    if not os.path.exists(file_path):
        print(f"[FAIL] Output file does not exist: {file_path}")
        sys.exit(1)
    print(f"[PASS] Processed output file exists: {file_path}")
    
    # Load the processed dataset
    try:
        df = pd.read_csv(file_path, dtype=str)
    except Exception as e:
        print(f"[FAIL] Failed to load the output file with pandas: {e}")
        sys.exit(1)
    print(f"[PASS] Successfully loaded dataset. Total rows: {len(df)}")
    
    if len(df) == 0:
        print("[FAIL] Output file is empty!")
        sys.exit(1)
        
    # 2. Check column schema
    expected_cols = [
        "application_number",
        "title",
        "field_of_invention",
        "classification_ipc",
        "applicant_name",
        "application_status",
        "publication_date"
    ]
    
    actual_cols = list(df.columns)
    if actual_cols != expected_cols:
        print(f"[FAIL] Column mismatch!")
        print(f"       Expected: {expected_cols}")
        print(f"       Actual:   {actual_cols}")
        sys.exit(1)
    print("[PASS] Column schema matches expectation.")
    
    # 3. Check for duplicates in application_number
    duplicate_count = df.duplicated(subset=["application_number"]).sum()
    if duplicate_count > 0:
        print(f"[FAIL] Found {duplicate_count} duplicate application numbers!")
        sys.exit(1)
    print("[PASS] Verified: Zero duplicate application numbers.")
    
    # 4. Check for rows where BOTH title and field_of_invention are missing/empty
    # We load them as string, check for NaN (pd.isna) or empty string (str.strip() == "")
    missing_both = df[
        (df["title"].isna() | (df["title"].str.strip() == "")) & 
        (df["field_of_invention"].isna() | (df["field_of_invention"].str.strip() == ""))
    ]
    if len(missing_both) > 0:
        print(f"[FAIL] Found {len(missing_both)} rows where BOTH title and field of invention are missing!")
        sys.exit(1)
    print("[PASS] Verified: No rows with empty title AND field of invention.")
    
    # 5. Check for null values in primary keys
    missing_keys = df["application_number"].isna() | (df["application_number"].str.strip() == "")
    if missing_keys.sum() > 0:
        print(f"[FAIL] Found {missing_keys.sum()} rows with missing application numbers!")
        sys.exit(1)
    print("[PASS] Verified: No missing application numbers.")
    
    # 6. Verify date format (YYYY-MM-DD or 'Unknown')
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    invalid_dates = df[
        ~df["publication_date"].astype(str).apply(lambda x: bool(date_pattern.match(x)) or x == "Unknown")
    ]
    if len(invalid_dates) > 0:
        print(f"[FAIL] Found {len(invalid_dates)} rows with invalid publication date formatting!")
        print("       First 5 invalid dates:")
        print(invalid_dates[["application_number", "publication_date"]].head())
        sys.exit(1)
    print("[PASS] Verified: All publication dates are in YYYY-MM-DD or 'Unknown' format.")
    
    # Print statistics
    print("\n==================================================")
    print("Dataset Validation Summary:")
    print("==================================================")
    print(f"Total Rows Checked : {len(df)}")
    print(f"Unique Applicants  : {df['applicant_name'].nunique()}")
    print(f"Unique Statuses    : {df['application_status'].nunique()}")
    
    unknown_dates = (df["publication_date"] == "Unknown").sum()
    pct_unknown_dates = (unknown_dates / len(df)) * 100
    print(f"Unknown Dates      : {unknown_dates} ({pct_unknown_dates:.2f}%)")
    
    unknown_fields = (df["field_of_invention"].isna() | (df["field_of_invention"] == "")).sum()
    pct_unknown_fields = (unknown_fields / len(df)) * 100
    print(f"Empty Fields       : {unknown_fields} ({pct_unknown_fields:.2f}%)")
    
    print("--------------------------------------------------")
    print("Status: ALL TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_validation()
