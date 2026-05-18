import logging
import numpy as np
import os
import sys
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances

# Add src to sys.path to allow imports from other modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

try:
    from utils.logger import logging
    from embeddings.embedder import generate_embeddings
except ImportError:
    import logging
    # Fallback or placeholder if embedder is not found during direct execution
    def generate_embeddings(texts, model=None):
        return np.random.rand(len(texts), 384)

def compute_cosine_similarity(vec1, vec2):
    """Computes cosine similarity between two vectors or sets of vectors."""
    return cosine_similarity(vec1, vec2)

def compute_dot_product(vec1, vec2):
    """Computes dot product between two vectors or sets of vectors."""
    # Ensure 2D for consistent behavior with sklearn-like output
    if vec1.ndim == 1: vec1 = vec1.reshape(1, -1)
    if vec2.ndim == 1: vec2 = vec2.reshape(1, -1)
    return np.dot(vec1, vec2.T)

def compute_euclidean_distance(vec1, vec2):
    """Computes Euclidean distance between two vectors or sets of vectors."""
    return pairwise_distances(vec1, vec2, metric='euclidean')

def cosine_similarity_matrix(embeddings):
    """
    Accepts a 2D numpy array and returns the full NxN cosine similarity matrix.
    Logs the matrix shape.
    """
    logging.info("Calculating cosine similarity matrix.")
    matrix = compute_cosine_similarity(embeddings, embeddings)
    logging.info(f"Cosine similarity matrix calculated. Shape: {matrix.shape}")
    return matrix

def multi_metric_search(query, corpus_texts, corpus_embeddings, model=None, top_n=3):
    """
    Generates an embedding for the query string, computes Cosine, Dot Product,
    and Euclidean Distance against all corpus embeddings, and prints a formatted
    table of results.
    """
    logging.info(f"Performing multi-metric search for query: '{query}'")
    
    # Generate query embedding
    query_embedding = generate_embeddings([query], model=model)
    
    # Calculate all metrics
    cos_sims = compute_cosine_similarity(query_embedding, corpus_embeddings).flatten()
    dot_prods = compute_dot_product(query_embedding, corpus_embeddings).flatten()
    euc_dists = compute_euclidean_distance(query_embedding, corpus_embeddings).flatten()
    
    # Get indices of top_n results based on Cosine Similarity
    top_indices = cos_sims.argsort()[-top_n:][::-1]
    
    results = []
    for rank, idx in enumerate(top_indices, 1):
        results.append({
            "rank": rank,
            "text": corpus_texts[idx],
            "cosine": float(cos_sims[idx]),
            "dot": float(dot_prods[idx]),
            "euclidean": float(euc_dists[idx])
        })
    
    # Print formatted table
    print(f"\n--- Multi-Metric Search Results for: '{query}' ---")
    header = f"{'Rank':<5} | {'Cosine':<8} | {'Dot':<8} | {'Euclidean':<10} | {'Text'}"
    print(header)
    print("-" * len(header))
    for res in results:
        text_snippet = (res['text'][:75] + '...') if len(res['text']) > 75 else res['text']
        print(f"{res['rank']:<5} | {res['cosine']:<8.4f} | {res['dot']:<8.4f} | {res['euclidean']:<10.4f} | {text_snippet}")
    
    logging.info(f"Multi-metric search completed. Found top {len(results)} matches.")
    return results

def semantic_search(query, corpus_texts, corpus_embeddings, model=None, top_n=3):
    """
    Generates an embedding for the query string, computes cosine similarity against
    all corpus embeddings, sorts results by score descending, and returns a list
    of dicts with keys rank, score, and text.
    """
    logging.info(f"Performing semantic search for query: '{query}'")
    
    # Generate query embedding
    query_embedding = generate_embeddings([query], model=model)
    
    # Calculate similarities
    similarities = compute_cosine_similarity(query_embedding, corpus_embeddings).flatten()
    
    # Get indices of top_n results
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    results = []
    for rank, idx in enumerate(top_indices, 1):
        results.append({
            "rank": rank,
            "score": float(similarities[idx]),
            "text": corpus_texts[idx]
        })
    
    logging.info(f"Semantic search completed. Found top {len(results)} matches.")
    return results

def compare_similarity_measures(text_a, text_b, text_c, model=None):
    """
    Generates embeddings for all three texts and returns a dict comparing
    cosine similarity, dot product, and euclidean distance between
    text_a vs text_b and text_a vs text_c.
    Logs all six values.
    """
    logging.info("Comparing similarity measures for three texts.")
    
    embeddings = generate_embeddings([text_a, text_b, text_c], model=model)
    emb_a = embeddings[0:1]
    emb_b = embeddings[1:2]
    emb_c = embeddings[2:3]
    
    # A vs B
    cos_ab = float(compute_cosine_similarity(emb_a, emb_b)[0][0])
    dot_ab = float(compute_dot_product(emb_a, emb_b)[0][0])
    euc_ab = float(compute_euclidean_distance(emb_a, emb_b)[0][0])
    
    # A vs C
    cos_ac = float(compute_cosine_similarity(emb_a, emb_c)[0][0])
    dot_ac = float(compute_dot_product(emb_a, emb_c)[0][0])
    euc_ac = float(compute_euclidean_distance(emb_a, emb_c)[0][0])
    
    logging.info(f"A vs B - Cosine: {cos_ab:.4f}, Dot: {dot_ab:.4f}, Euclidean: {euc_ab:.4f}")
    logging.info(f"A vs C - Cosine: {cos_ac:.4f}, Dot: {dot_ac:.4f}, Euclidean: {euc_ac:.4f}")
    
    return {
        "a_vs_b": {
            "cosine": cos_ab,
            "dot_product": dot_ab,
            "euclidean": euc_ab
        },
        "a_vs_c": {
            "cosine": cos_ac,
            "dot_product": dot_ac,
            "euclidean": euc_ac
        }
    }
