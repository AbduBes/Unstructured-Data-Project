import pandas as pd
import logging
from typing import List, Dict, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

def semantic_search(query: str, collection, n_results: int = 5, filters: Optional[Dict] = None) -> pd.DataFrame:
    """Performs semantic search using ChromaDB and returns a formatted DataFrame."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=filters
    )
    
    formatted_data = []
    ids = results['ids'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    for i in range(len(ids)):
        m = metadatas[i]
        formatted_data.append({
            'rank': i + 1,
            'title': m.get('title', 'Unknown'),
            'author_name': m.get('author_name', 'N/A'),
            'primary_genre': m.get('primary_genre', 'N/A'),
            'language': m.get('language', 'N/A'),
            'rating': m.get('rating', 0.0),
            'first_publish_year': m.get('first_publish_year', 'N/A'),
            'distance_score': round(distances[i], 4)
        })
        
    df = pd.DataFrame(formatted_data)
    logger.info(f"Semantic search query: '{query}' returned {len(df)} results.")
    return df

def keyword_search(query: str, df: pd.DataFrame, columns: List[str] = ['title', 'author_name', 'overview', 'genres'], n_results: int = 5) -> pd.DataFrame:
    """Performs case-insensitive keyword search across specified columns and returns top results sorted by rating."""
    query_lower = query.lower()
    mask = pd.Series([False] * len(df))
    
    for col in columns:
        if col in df.columns:
            mask |= df[col].astype(str).str.lower().str.contains(query_lower, na=False)
            
    matches = df[mask].sort_values(by='rating', ascending=False).head(n_results)
    
    result_df = matches[['title', 'author_name', 'primary_genre', 'language', 'rating', 'first_publish_year']].reset_index(drop=True)
    
    logger.info(f"Keyword search query: '{query}' in columns {columns} returned {len(result_df)} matches.")
    return result_df

def compare_search(query: str, collection, df: pd.DataFrame, n_results: int = 5) -> Dict[str, pd.DataFrame]:
    """Compares semantic and keyword search results side-by-side."""
    sem_res = semantic_search(query, collection, n_results)
    key_res = keyword_search(query, df, n_results=n_results)
    
    print(f"\n--- Search Comparison for: '{query}' ---")
    print(f"\n[Semantic Results]:\n{sem_res.to_string(index=False)}")
    print(f"\n[Keyword Results]:\n{key_res.to_string(index=False)}")
    
    logger.info(f"Comparison search performed for query: '{query}'")
    return {'semantic': sem_res, 'keyword': key_res}
