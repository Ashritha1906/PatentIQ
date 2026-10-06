import os
import re
import numpy as np
import logging
from backend.retrieval.search_patents import get_retrieval_resources

logger = logging.getLogger("ConceptClustering")

def clean_words(text):
    """
    Cleans text and extracts meaningful words (len > 4, non-stopword).
    """
    stopwords = {
        "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
        "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
        "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
        "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
        "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
        "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into",
        "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
        "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
        "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
        "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs",
        "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
        "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
        "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
        "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
        "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
        "yourselves", "system", "method", "apparatus", "device", "process", "systems", "methods", "devices"
    }
    
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    return [w for w in words if w not in stopwords]

def generate_cluster_name(patents_in_cluster):
    """
    Determines a logical cluster name based on dominant field of invention and title keywords.
    """
    if not patents_in_cluster:
        return "General Technologies"
        
    # Get fields of invention
    fields = [p.get("field_of_invention", "Unknown") for p in patents_in_cluster]
    dominant_field = max(set(fields), key=fields.count)
    
    # Capitalize dominant field nicely
    dominant_field = dominant_field.replace("_", " ").title()
    
    # Get top title keywords
    all_words = []
    for p in patents_in_cluster:
        all_words.extend(clean_words(p.get("title", "")))
        all_words.extend(clean_words(p.get("field_of_invention", "")))
        
    if all_words:
        word_counts = {}
        for w in all_words:
            word_counts[w] = word_counts.get(w, 0) + 1
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        top_k_words = [w[0].capitalize() for w in sorted_words[:2]]
        return f"{dominant_field} ({' '.join(top_k_words)})"
        
    return dominant_field

def perform_clustering(retrieved_patents, num_clusters=3, db_path="data/vectordb"):
    """
    Programmatically clusters retrieved patents using cosine distance on SentenceTransformer embeddings.
    """
    n_samples = len(retrieved_patents)
    if n_samples == 0:
        return {}
        
    num_clusters = min(num_clusters, n_samples)
    
    # Load model to encode patent brief contexts
    model, _ = get_retrieval_resources(db_path)
    texts = [f"{p['title']} {p['field_of_invention']} {p.get('patent_text', '')[:200]}" for p in retrieved_patents]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    
    # Standardize norms
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norm_embeddings = embeddings / (norms + 1e-9)
    
    # Deterministic initial centroid indices (evenly spaced)
    step = max(1, n_samples // num_clusters)
    centroid_indices = [i * step for i in range(num_clusters)]
    centroid_indices = centroid_indices[:num_clusters]
    
    centroids = norm_embeddings[centroid_indices].copy()
    
    # Run simple K-means (10 iterations)
    assignments = np.zeros(n_samples, dtype=int)
    for _ in range(10):
        # Distance calculation via dot product (cosine similarity)
        similarities = np.dot(norm_embeddings, centroids.T)
        new_assignments = np.argmax(similarities, axis=1)
        if np.array_equal(assignments, new_assignments):
            break
        assignments = new_assignments
        
        # Update centroids
        for k in range(num_clusters):
            members = norm_embeddings[assignments == k]
            if len(members) > 0:
                mean_val = np.mean(members, axis=0)
                centroids[k] = mean_val / (np.linalg.norm(mean_val) + 1e-9)
                
    # Compile assignments
    clusters = {}
    for idx, cluster_id in enumerate(assignments):
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(retrieved_patents[idx])
        
    return clusters

def generate_concept_map_and_landscape(retrieved_patents, db_path="data/vectordb"):
    """
    Generates concept clustering information containing:
      - concept_clusters: dict of assigned clusters
      - concept_map: visual tree-like text representation
      - cluster_summary: details on each group
      - technology_landscape: descriptive paragraph of the thematic clusters
    """
    if not retrieved_patents:
        return {
            "concept_clusters": {},
            "concept_map": "No patents available to cluster.",
            "cluster_summary": "Empty retrieved set.",
            "technology_landscape": "No patents found."
        }
        
    clusters = perform_clustering(retrieved_patents, num_clusters=3, db_path=db_path)
    
    # Process clusters and name them
    processed_clusters = {}
    map_lines = ["Concept Map (retrieved patents grouped by theme):", "└── Root (PatentIQ Search Results)"]
    summary_lines = []
    
    cluster_descriptions = []
    for c_id, patents in sorted(clusters.items()):
        c_name = generate_cluster_name(patents)
        processed_clusters[c_name] = [p["application_number"] for p in patents]
        
        # Build Concept Map Lines
        map_lines.append(f"    ├── Cluster {c_id + 1}: {c_name}")
        for pat in patents:
            map_lines.append(f"    │   └── Patent ID: {pat['application_number']} - {pat['title'][:60]}...")
            
        # Build Cluster Summary lines
        summary_lines.append(f"Cluster {c_id + 1}: {c_name}")
        summary_lines.append(f"  Includes: {', '.join(p['application_number'] for p in patents)}")
        p_titles = [f"'{p['title']}'" for p in patents[:2]]
        summary_lines.append(f"  Core Focus: Analyzes technology related to {c_name.split('(')[0].strip()}, focusing on patents such as {', '.join(p_titles)}.")
        summary_lines.append("--------------------------------------------------")
        
        cluster_descriptions.append(f"{c_name} (containing {len(patents)} patents)")
        
    concept_map = "\n".join(map_lines)
    cluster_summary = "\n".join(summary_lines)
    
    # Technology Landscape Summary paragraph
    landscape = (
        f"The retrieved patent landscape is divided into {len(clusters)} distinct thematic clusters, "
        f"namely: {', '.join(cluster_descriptions)}. This indicates that the surrounding patent space "
        f"concentrates primarily in these domains, which set the state-of-the-art parameters for the user's idea."
    )
    
    return {
        "concept_clusters": processed_clusters,
        "concept_map": concept_map,
        "cluster_summary": cluster_summary,
        "technology_landscape": landscape
    }
