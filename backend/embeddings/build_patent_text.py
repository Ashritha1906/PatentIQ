import os
import sys
import re
import pandas as pd

def clean_text(text):
    """
    Cleans raw text by removing non-printable control characters,
    replacing replacement characters like , and normalizing multiple whitespaces.
    """
    if pd.isna(text) or not isinstance(text, str):
        return ""
    
    # Remove unicode control characters (categories Cc, Cf, Cs, Co, Cn)
    # isprintable() checks for non-printable characters
    cleaned = "".join(ch for ch in text if ch.isprintable())
    
    # Replace Unicode replacement characters
    cleaned = cleaned.replace('\ufffd', '')
    
    # Normalize all whitespaces (spaces, tabs, multiple newlines) to a single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()

def build_representation(row):
    """
    Constructs the semantic patent text using the specified template:
    Title: {title}

    Field Of Invention: {field_of_invention}

    IPC Classification: {classification_ipc}

    Applicant: {applicant_name}
    """
    title = clean_text(row.get('title'))
    field = clean_text(row.get('field_of_invention'))
    ipc = clean_text(row.get('classification_ipc'))
    applicant = clean_text(row.get('applicant_name'))
    
    # Sensible defaults for empty fields
    title = title if title else "Unknown Title"
    field = field if field else "Unknown Field"
    ipc = ipc if ipc else "Unknown IPC"
    applicant = applicant if applicant else "Unknown Applicant"
    
    # Specified template format
    return (
        f"Title: {title}\n\n"
        f"Field Of Invention: {field}\n\n"
        f"IPC Classification: {ipc}\n\n"
        f"Applicant: {applicant}"
    )

def main():
    print("==================================================")
    print("PatentIQ - Running Patent Text Construction")
    print("==================================================")
    
    input_path = os.path.join("data", "processed", "all_patents.csv")
    output_path = os.path.join("data", "processed", "patent_text_dataset.csv")
    
    if not os.path.exists(input_path):
        print(f"[ERROR] Input dataset not found: {input_path}")
        sys.exit(1)
        
    print(f"Loading preprocessed dataset from: {input_path}")
    df = pd.read_csv(input_path)
    total_records = len(df)
    print(f"Loaded {total_records} patent records.")
    
    # Log initial missing value statistics
    print("\nInitial dataset missing value counts:")
    for col in df.columns:
        missing_cnt = df[col].isna().sum()
        missing_pct = (missing_cnt / total_records) * 100
        print(f"  {col}: {missing_cnt} ({missing_pct:.4f}%)")
        
    print("\nGenerating cleaned patent_text representations...")
    df['patent_text'] = df.apply(build_representation, axis=1)
    
    # Verify the results
    text_lengths = df['patent_text'].str.len()
    print("\nText Representation Length Statistics:")
    print(f"  Average Character Length : {text_lengths.mean():.2f}")
    print(f"  Minimum Character Length : {text_lengths.min()}")
    print(f"  Maximum Character Length : {text_lengths.max()}")
    
    # Save the dataset
    print(f"\nSaving dataset with patent_text column to: {output_path}")
    df.to_csv(output_path, index=False)
    
    print("\nSample processed record (index 0):")
    print("--------------------------------------------------")
    print(df.loc[0, 'patent_text'])
    print("--------------------------------------------------")
    
    print("\nPatent text construction completed successfully!")
    print("==================================================")

if __name__ == '__main__':
    main()
