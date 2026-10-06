#!/usr/bin/env python3
"""
PatentIQ - Phase 1: Data Preprocessing Script
This script merges, cleans, and standardizes the patent datasets (2010, 2011, and 2019)
to create a clean consolidated dataset for semantic search and RAG indexing.

Author: Antigravity AI Mentor
"""

import os
import argparse
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("preprocess")


def clean_text_field(text):
    """
    Cleans a text field by stripping whitespace, removing outer quotes,
    and resolving common delimiter formatting issues.
    """
    if pd.isna(text):
        return ""
    
    text = str(text).strip()
    
    # Remove surrounding double/triple quotes if they were poorly escaped
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    
    # Strip any additional outer quotes that might remain from multiple escapes
    text = text.strip('"').strip("'").strip()
    
    # Clean up internal extra spaces
    text = " ".join(text.split())
    return text


def clean_separated_names(name_string):
    """
    Patent datasets represent lists of inventors/applicants separated by hashes (e.g., #Name1#Name2).
    This function converts "#Name1#Name2" to "Name1; Name2" for cleaner text and better RAG parsing.
    """
    if pd.isna(name_string) or str(name_string).strip() == "":
        return "Unknown"
        
    s = str(name_string).strip()
    if s.startswith("#"):
        s = s[1:]
    if s.endswith("#"):
        s = s[:-1]
        
    # Split by hash and join with semicolon
    names = [name.strip() for name in s.split("#") if name.strip()]
    if not names:
        return "Unknown"
    return "; ".join(names)


def parse_patent_date(date_str):
    """
    Attempts to parse dates in DD/MM/YYYY format and standardizes to YYYY-MM-DD.
    Handles empty values, NaT, and malformed strings.
    """
    if pd.isna(date_str):
        return pd.NaT
        
    date_str = str(date_str).strip()
    if date_str in ["", "--", "-", "N/A", "nan"]:
        return pd.NaT
        
    # Common formats observed: DD/MM/YYYY, YYYY-MM-DD
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
            
    # Fallback to pandas automatic parsing (with dayfirst=True since Indian patents are DD/MM/YYYY)
    try:
        return pd.to_datetime(date_str, dayfirst=True, errors='coerce')
    except Exception:
        return pd.NaT


def preprocess_datasets(raw_dir, output_file):
    """
    Main pipeline function to load raw CSVs, clean, merge, and save.
    """
    logger.info("Initializing PatentIQ Data Engineering Pipeline...")
    
    # Define expected raw files
    raw_files = ["2010.csv", "2011.csv", "2019.csv"]
    file_paths = [os.path.join(raw_dir, f) for f in raw_files]
    
    # Verify files exist
    missing_files = [path for path in file_paths if not os.path.exists(path)]
    if missing_files:
        raise FileNotFoundError(f"Missing required raw files: {missing_files}")
        
    dataframes = []
    
    # Column mapping dictionary
    column_mapping = {
        "Application Number": "application_number",
        "Title": "title",
        "Field Of Invention": "field_of_invention",
        "Classification (IPC)": "classification_ipc",
        "Applicant Name": "applicant_name",
        "Application Status": "application_status",
        "Publication Date(U/S 11A)": "publication_date"
    }
    
    cols_to_use = list(column_mapping.keys())
    
    # 1. Load each CSV file
    for file_name, file_path in zip(raw_files, file_paths):
        logger.info(f"Loading raw dataset: {file_name}...")
        
        # Try reading file, handling potential encoding issues (e.g. latin-1 fallback)
        try:
            df = pd.read_csv(file_path, usecols=cols_to_use, encoding='utf-8')
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 decode failed for {file_name}. Falling back to Windows-1252 encoding.")
            df = pd.read_csv(file_path, usecols=cols_to_use, encoding='cp1252')
        except ValueError as ve:
            # If standard columns are not found, let's load all columns first and check
            logger.warning(f"Could not load specified columns directly: {ve}. Loading all columns to debug.")
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='cp1252')
            
            # Keep only columns that exist
            existing_cols = [col for col in cols_to_use if col in df.columns]
            df = df[existing_cols]
            logger.info(f"Loaded columns: {existing_cols}")
            
        logger.info(f"Successfully loaded {file_name} with {df.shape[0]} rows.")
        dataframes.append(df)
        
    # 2. Merge all datasets
    logger.info("Merging datasets...")
    merged_df = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Merged dataset shape: {merged_df.shape[0]} rows, {merged_df.shape[1]} columns.")
    
    # 3. Rename columns to standardized snake_case
    merged_df = merged_df.rename(columns=column_mapping)
    
    # Ensure all required columns exist in the dataframe (fill with NaN if missing)
    required_cols = list(column_mapping.values())
    for col in required_cols:
        if col not in merged_df.columns:
            logger.warning(f"Column '{col}' was missing in raw data. Creating empty column.")
            merged_df[col] = np.nan
            
    # Keep only the standardized columns
    merged_df = merged_df[required_cols]
    
    # 4. Handle Missing Values & Core Validation
    initial_row_count = len(merged_df)
    
    # Clean string columns and handle formatting
    logger.info("Cleaning text fields and standardizing delimiters...")
    merged_df["application_number"] = merged_df["application_number"].astype(str).str.strip()
    
    # Drop rows without application number
    merged_df = merged_df[merged_df["application_number"].notna() & (merged_df["application_number"] != "") & (merged_df["application_number"] != "nan")]
    after_app_num_clean = len(merged_df)
    logger.info(f"Removed {initial_row_count - after_app_num_clean} rows due to missing Application Number.")
    
    # Clean Title and Field of Invention
    merged_df["title"] = merged_df["title"].apply(clean_text_field)
    merged_df["field_of_invention"] = merged_df["field_of_invention"].apply(clean_text_field)
    
    # Drop rows where BOTH title and field of invention are missing/empty
    # Because we cannot generate meaningful embeddings for semantic search if there is no text
    merged_df = merged_df[~((merged_df["title"] == "") & (merged_df["field_of_invention"] == ""))]
    after_text_clean = len(merged_df)
    logger.info(f"Removed {after_app_num_clean - after_text_clean} rows where BOTH Title and Field of Invention were missing.")
    
    # Clean Applicant Name list
    merged_df["applicant_name"] = merged_df["applicant_name"].apply(clean_separated_names)
    
    # Fill remaining string columns with default "Unknown" or format them
    merged_df["classification_ipc"] = merged_df["classification_ipc"].apply(clean_text_field).replace("", "Unknown")
    merged_df["application_status"] = merged_df["application_status"].apply(clean_text_field).replace("", "Unknown")
    
    # 5. Remove duplicates based on Application Number
    logger.info("Removing duplicates based on Application Number...")
    merged_df = merged_df.sort_values(by=["application_number", "publication_date"], na_position='last')
    
    # Remove duplicates, keeping the first occurrence
    pre_dedup_count = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=["application_number"], keep="first")
    post_dedup_count = len(merged_df)
    logger.info(f"Removed {pre_dedup_count - post_dedup_count} duplicate rows. {post_dedup_count} rows remain.")
    
    # 6. Standardize date format
    logger.info("Parsing and standardizing Publication Dates...")
    parsed_dates = merged_df["publication_date"].apply(parse_patent_date)
    # Convert to YYYY-MM-DD string format (or NaN as empty string)
    merged_df["publication_date"] = parsed_dates.dt.strftime("%Y-%m-%d").fillna("Unknown")
    
    # 7. Final Checks & Save
    logger.info("Preprocessed dataset summary statistics:")
    logger.info(f"  - Total processed patents: {len(merged_df)}")
    logger.info(f"  - Unique applicants: {merged_df['applicant_name'].nunique()}")
    logger.info(f"  - Missing publication dates: {sum(merged_df['publication_date'] == 'Unknown')}")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        logger.info(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
    logger.info(f"Saving cleaned dataset to: {output_file}...")
    merged_df.to_csv(output_file, index=False, encoding='utf-8')
    logger.info("Phase 1 Preprocessing completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess and merge PatentIQ datasets.")
    parser.add_argument(
        "--raw-dir",
        type=str,
        default=os.path.join("data", "raw"),
        help="Directory containing the raw CSV files"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=os.path.join("data", "processed", "all_patents.csv"),
        help="File path to save the preprocessed CSV output"
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    preprocess_datasets(args.raw_dir, args.output_file)
