import logging
import pandas as pd
import numpy as np
import os
import sys
from sentence_transformers import SentenceTransformer

# Add src to sys.path to allow imports from other modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

try:
    from utils.logger import logging
except ImportError:
    import logging

def load_model(model_name='all-MiniLM-L6-v2'):
    """
    Loads and returns the SentenceTransformer model with a log message.
    """
    logging.info(f"Loading SentenceTransformer model: {model_name}")
    return SentenceTransformer(model_name)

# Load the model once at module level so it is reused across calls
MODEL = load_model('all-MiniLM-L6-v2')

def generate_embeddings(texts, model=None):
    """
    Accepts a list of strings, loads the default model if none is passed,
    calls model.encode() and returns a numpy array.
    Logs the input count and output shape.
    """
    if model is None:
        model = MODEL
    
    logging.info(f"Generating embeddings for {len(texts)} texts.")
    embeddings = model.encode(texts)
    
    # Ensure it's a numpy array
    embeddings_array = np.array(embeddings)
    logging.info(f"Embeddings generated. Output shape: {embeddings_array.shape}")
    
    return embeddings_array

def combine_book_fields(df):
    """
    Concatenates title, author_name, genres, and overview into a single descriptive string per row.
    Format: 'Title: {title}. Author: {author_name}. Genres: {genres}. Overview: {overview}'
    Handles missing values by filling them with empty strings.
    Returns a pandas Series.
    """
    logging.info("Combining book fields into descriptive strings for embedding.")
    
    # Fill missing values with empty strings
    df_filled = df.fillna('')
    
    # Concatenate fields into the specified format
    combined = df_filled.apply(
        lambda row: f"Title: {row.get('title', '')}. Author: {row.get('author_name', '')}. Genres: {row.get('genres', '')}. Overview: {row.get('overview', '')}",
        axis=1
    )
    
    return combined
