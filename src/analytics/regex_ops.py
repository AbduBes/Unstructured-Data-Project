import pandas as pd
import logging
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analytics.data_loader import get_mongo_data

# Ensure logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_starts_with_the(df: pd.DataFrame) -> pd.DataFrame:
    df['title_starts_the'] = df['title'].str.contains(r'^The', regex=True, na=False)
    logging.info("Regex: Found titles starting with 'The'")
    return df

def extract_first_subject_word(df: pd.DataFrame) -> pd.DataFrame:
    df['first_subject_word'] = df['subject'].str.extract(r'^(\w+)', expand=False)
    logging.info("Regex: Extracted first word of subject")
    return df

def clean_subtitle(df: pd.DataFrame) -> pd.DataFrame:
    df['subtitle_clean'] = df['subtitle'].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
    logging.info("Regex: Replaced non-alphanumeric in subtitle")
    return df

def identify_dune_titles(df: pd.DataFrame) -> pd.DataFrame:
    dune_regex = re.compile(r'dune', re.IGNORECASE)
    df['is_dune'] = df['title'].apply(lambda x: bool(dune_regex.search(str(x))))
    logging.info("Regex: Found titles containing 'Dune' (case insensitive)")
    return df

def run_regex_operations():
    logging.info("=== Starting Regex Operations ===")
    
    # Load data
    df = get_mongo_data()
    
    print("\n--- Regex Operations ---")
    
    df = extract_starts_with_the(df)
    df = extract_first_subject_word(df)
    df = clean_subtitle(df)
    df = identify_dune_titles(df)
    
    print(df[['title', 'title_starts_the', 'first_subject_word', 'is_dune']].head())
    
    logging.info("=== Regex Operations Completed ===")
    return df

if __name__ == "__main__":
    run_regex_operations()
