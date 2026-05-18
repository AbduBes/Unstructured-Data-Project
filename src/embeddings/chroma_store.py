import os
import sys
import logging
import pandas as pd
import numpy as np
import chromadb
from chromadb.config import Settings

# Add src to sys.path to allow imports from other modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

try:
    from utils.logger import logging
    from embeddings.embedder import combine_book_fields
except ImportError:
    import logging
    # Fallback for combine_book_fields if not found
    def combine_book_fields(df):
        return df.apply(lambda x: "Fallback document", axis=1)

def get_client(path='data/embeddings/chroma_db'):
    """
    Creates the directory if it does not exist, initialises and returns a PersistentClient.
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logging.info(f"Created directory for ChromaDB: {path}")
    
    logging.info(f"Initialising ChromaDB PersistentClient at: {path}")
    return chromadb.PersistentClient(path=path)

def get_or_create_collection(client, name='books', reset=False):
    """
    Deletes and recreates the collection if reset=True, otherwise gets or creates it.
    Uses cosine similarity as the distance metric.
    """
    if reset:
        try:
            client.delete_collection(name=name)
            logging.info(f"Deleted existing collection: {name}")
        except Exception:
            logging.info(f"Collection {name} did not exist, nothing to delete.")
    
    # Check if it exists to log correctly
    existing_collections = [c.name for c in client.list_collections()]
    status = "Loaded existing" if name in existing_collections and not reset else "Created new"
    
    collection = client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )
    
    logging.info(f"{status} collection: {name} with cosine similarity.")
    return collection

def add_books(collection, df, embeddings):
    """
    Adds books to the Chroma collection.
    Builds documents, ids, and metadatas lists.
    """
    logging.info(f"Preparing to add {len(df)} books to ChromaDB collection.")
    
    # 1. Build documents list
    documents = combine_book_fields(df).tolist()
    
    # 2. Build IDs list (cast key column to string)
    ids = df['key'].astype(str).tolist()
    
    # 3. Build metadatas list with specific defaults
    metadatas = []
    for _, row in df.iterrows():
        meta = {
            "title": str(row.get('title', 'Unknown')),
            "author_name": str(row.get('author_name', 'Unknown')),
            "primary_genre": str(row.get('primary_genre', 'Unknown')),
            "language": str(row.get('language', 'Unknown')),
            "first_publish_year": int(row.get('first_publish_year', 0)) if pd.notnull(row.get('first_publish_year')) else 0,
            "rating": float(row.get('rating', 0.0)) if pd.notnull(row.get('rating')) else 0.0,
            "ratings_count": float(row.get('ratings_count', 0.0)) if pd.notnull(row.get('ratings_count')) else 0.0,
            "edition_count": int(row.get('edition_count', 0)) if pd.notnull(row.get('edition_count')) else 0
        }
        metadatas.append(meta)
    
    # 4. Convert embeddings to nested lists if they are numpy arrays
    if isinstance(embeddings, np.ndarray):
        embeddings_list = embeddings.tolist()
    else:
        embeddings_list = embeddings
    
    # 5. Add to collection
    collection.add(
        documents=documents,
        embeddings=embeddings_list,
        metadatas=metadatas,
        ids=ids
    )
    
    logging.info(f"Successfully added {len(ids)} books to the collection.")

def get_collection_info(collection):
    """
    Returns a dict with name, count, and sample of the first three ids.
    """
    count = collection.count()
    # Safely get sample IDs
    sample_data = collection.peek(limit=3)
    sample_ids = sample_data.get('ids', [])
    
    info = {
        "name": collection.name,
        "count": count,
        "sample_ids": sample_ids
    }
    
    logging.info(f"Collection '{collection.name}' contains {count} items.")
    return info
