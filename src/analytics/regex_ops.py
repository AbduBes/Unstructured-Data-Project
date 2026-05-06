import pandas as pd
import logging
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analytics.data_loader import get_mongo_data

# Ensure logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_regex_operations():
    logging.info("=== Starting Regex Operations ===")
    
    # Load data
    df = get_mongo_data()
    
    # Rename for task compliance (Movie Dataset context)
    df = df.rename(columns={
        'subject': 'genres',
        'subtitle': 'overview',
        'ratings_average': 'rating'
    })
    
    print("\n--- Regex Operations ---")
    
    # 1. Find titles starting with 'The'
    df['title_starts_the'] = df['title'].str.contains(r'^The', regex=True, na=False)
    logging.info("Regex 1: Found titles starting with 'The'")
    
    # 2. Extract first word of genres
    df['first_genre_word'] = df['genres'].str.extract(r'^(\w+)', expand=False)
    logging.info("Regex 2: Extracted first word of genres")
    
    # 3. Replace non-alphanumeric in overview
    df['overview_clean'] = df['overview'].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
    logging.info("Regex 3: Replaced non-alphanumeric in overview")
    
    # 4. Find titles containing 'Dune' (case insensitive)
    dune_regex = re.compile(r'dune', re.IGNORECASE)
    df['is_dune'] = df['title'].apply(lambda x: bool(dune_regex.search(str(x))))
    logging.info("Regex 4: Found titles containing 'Dune' (case insensitive)")
    
    print(df[['title', 'title_starts_the', 'first_genre_word', 'is_dune']].head())
    
    logging.info("=== Regex Operations Completed ===")
    return df

if __name__ == "__main__":
    run_regex_operations()
