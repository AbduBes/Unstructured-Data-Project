import os
import sys
import pandas as pd
import numpy as np

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from utils.logger import logging
from embeddings.chroma_store import get_client

def demonstrate_filters():
    """Demonstrates metadata filtering using $eq, $gte, $in, and $and."""
    logging.info("=== Starting ChromaDB Metadata Filtering Demonstration ===")
    
    # Initialize client and get collection
    client = get_client(path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embeddings', 'chroma_db')))
    collection = client.get_collection(name='books_collection')
    
    query_text = "space exploration and alien life"
    
    # 1. $eq operator: Exact match for language
    logging.info("1. Testing $eq operator (Language: eng)")
    res_eq = collection.query(
        query_texts=[query_text],
        n_results=3,
        where={"language": {"$eq": "eng"}}
    )
    print_results("Equality Filter ($eq: eng)", res_eq)
    
    # 2. $gte operator: Year >= 2000
    logging.info("2. Testing $gte operator (Year >= 2000)")
    res_gte = collection.query(
        query_texts=[query_text],
        n_results=3,
        where={"first_publish_year": {"$gte": 2000}}
    )
    print_results("Greater Than or Equal Filter ($gte: 2000)", res_gte)
    
    # 3. $in operator: Multiple genres
    logging.info("3. Testing $in operator (Genre in [Fiction, Science Fiction])")
    # Note: Using common genres based on typical Open Library data
    res_in = collection.query(
        query_texts=[query_text],
        n_results=3,
        where={"primary_genre": {"$in": ["Fiction", "Science Fiction", "American science fiction"]}}
    )
    print_results("In-list Filter ($in: Fiction/Sci-Fi)", res_in)
    
    # 4. $and operator: Combined conditions
    logging.info("4. Testing $and operator (Language: eng AND Rating >= 4.0)")
    res_and = collection.query(
        query_texts=[query_text],
        n_results=3,
        where={"$and": [
            {"language": {"$eq": "eng"}},
            {"rating": {"$gte": 4.0}}
        ]}
    )
    print_results("Logical AND Filter ($and: eng + rating >= 4.0)", res_and)

def print_results(title, results):
    print(f"\n--- {title} ---")
    if not results['ids'] or not results['ids'][0]:
        print("No matches found.")
        return
        
    for i in range(len(results['ids'][0])):
        meta = results['metadatas'][0][i]
        dist = results['distances'][0][i]
        print(f"Rank {i+1}: {meta.get('title', 'Unknown')} | Year: {meta.get('first_publish_year')} | Genre: {meta.get('primary_genre')} | Lang: {meta.get('language')} | Rating: {meta.get('rating')} | Dist: {dist:.4f}")

if __name__ == "__main__":
    demonstrate_filters()
