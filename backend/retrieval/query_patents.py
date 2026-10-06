import os
import sys
from backend.retrieval.hybrid_search import hybrid_search

def clean_input(prompt):
    try:
        val = input(prompt).strip()
        return val if val else None
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        sys.exit(0)

def main():
    print("==================================================")
    print("PatentIQ - Interactive Patent Retrieval CLI")
    print("==================================================")
    print("Initializing retrieval systems...")
    
    # Warm up caches
    from backend.retrieval.search_patents import get_retrieval_resources
    try:
        get_retrieval_resources()
        print("Retrieval engine initialized and ready.")
    except Exception as e:
        print(f"[ERROR] Failed to load retrieval resources: {e}")
        sys.exit(1)
        
    while True:
        print("\n==================================================")
        query = clean_input("Enter your invention idea (or type 'exit' to quit): ")
        
        if not query:
            continue
            
        if query.lower() in ['exit', 'quit']:
            print("Thank you for using PatentIQ. Exiting.")
            break
            
        # Optional filtering
        apply_filters = clean_input("Do you want to apply metadata filters? (y/N): ")
        field_filter = None
        ipc_filter = None
        applicant_filter = None
        
        if apply_filters and apply_filters.lower() in ['y', 'yes']:
            print("  --- Configure Filters (Leave blank to skip) ---")
            field_filter = clean_input("  Invention Field (e.g. COMPUTER SCIENCE): ")
            ipc_filter = clean_input("  IPC Classification (e.g. G06F): ")
            applicant_filter = clean_input("  Applicant Name (e.g. QUALCOMM INCORPORATED): ")
            
        top_k_str = clean_input("Enter number of results to return (default is 5): ")
        top_k = 5
        if top_k_str:
            try:
                top_k = int(top_k_str)
            except ValueError:
                print("  [WARNING] Invalid number. Defaulting to 5.")
                
        print("\nSearching patent corpus...")
        try:
            results = hybrid_search(
                query=query,
                top_k=top_k,
                field_filter=field_filter,
                ipc_filter=ipc_filter,
                applicant_filter=applicant_filter
            )
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            continue
            
        if not results:
            print("No matching patents found. Try relaxing your filters.")
            continue
            
        print(f"\nTop {len(results)} Matching Patents:")
        print("--------------------------------------------------")
        for i, res in enumerate(results):
            print(f"[{i+1}] Title : {res['title']}")
            print(f"    Score : {res['similarity_score']:.4f} (Distance: {res['distance']:.4f})")
            print(f"    Field : {res['field_of_invention']}")
            print(f"    IPC   : {res['classification_ipc']}")
            print(f"    Assign: {res['applicant_name']}")
            print(f"    ID    : {res['application_number']}")
            print("--------------------------------------------------")

if __name__ == '__main__':
    main()
