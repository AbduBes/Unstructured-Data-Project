import pandas as pd
import logging
from typing import List, Dict, Union
from src.embeddings.search_engine import semantic_search, keyword_search

# Configure logging
logger = logging.getLogger(__name__)

def reciprocal_rank_fusion(ranked_lists: List[List[str]], k: int = 60) -> Dict[str, float]:
    """Computes RRF score for a list of ranked lists."""
    rrf_scores = {}
    for ranked_list in ranked_lists:
        for rank, item_id in enumerate(ranked_list, start=1):
            score = 1.0 / (k + rank)
            rrf_scores[item_id] = rrf_scores.get(item_id, 0.0) + score
    
    # Sort by score descending
    return dict(sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True))

def hybrid_search(query: str, collection, df: pd.DataFrame, n_results: int = 5, k: int = 60, semantic_weight: float = 0.5, keyword_weight: float = 0.5) -> pd.DataFrame:
    """Combines semantic and keyword search results using weighted RRF."""
    # Get wider candidate pool
    sem_df = semantic_search(query, collection, n_results=n_results * 2)
    key_df = keyword_search(query, df, n_results=n_results * 2)
    
    # Assume ID is not explicitly in DataFrame; map via title or similar unique identifier if possible.
    # Note: Using 'title' as a proxy for ID based on the provided search_engine output.
    sem_ids = sem_df['title'].tolist()
    key_ids = key_df['title'].tolist()
    
    # RRF fusion
    rrf_scores = reciprocal_rank_fusion([sem_ids, key_ids], k=k)
    
    # Create final results
    results = []
    for title, score in rrf_scores.items():
        row = df[df['title'] == title].iloc[0]
        results.append({
            'title': title,
            'author_name': row['author_name'],
            'primary_genre': row['primary_genre'],
            'language': row['language'],
            'rating': row['rating'],
            'first_publish_year': row['first_publish_year'],
            'combined_score': round(score, 4)
        })
    
    final_df = pd.DataFrame(results).head(n_results)
    logger.info(f"Hybrid search query: '{query}' | Candidates: {len(rrf_scores)} | Results: {len(final_df)}")
    return final_df

def compare_all_methods(query: str, collection, df: pd.DataFrame, n_results: int = 5) -> Dict[str, pd.DataFrame]:
    """Compares keyword, semantic, and hybrid search methods."""
    key_res = keyword_search(query, df, n_results=n_results)
    sem_res = semantic_search(query, collection, n_results=n_results)
    hyb_res = hybrid_search(query, collection, df, n_results=n_results)
    
    logger.info(f"Comparison search performed for query: '{query}'")
    return {'keyword': key_res, 'semantic': sem_res, 'hybrid': hyb_res}
