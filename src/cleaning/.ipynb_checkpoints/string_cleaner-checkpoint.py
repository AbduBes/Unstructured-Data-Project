import pandas as pd
import re
import logging

def clean_strings(df):
    """Fixes whitespace, casing, and formatting inconsistencies."""
    logging.info("Starting string cleaning...")
    
    # Whitespace and Casing for Title
    if 'title' in df.columns:
        df['title'] = df['title'].str.strip().str.title()
        logging.info("Cleaned 'title' column (stripped and title-cased)")

    # Lowercase and strip for Language
    if 'language' in df.columns:
        df['language'] = df['language'].str.strip().str.lower()
        logging.info("Cleaned 'language' column (stripped and lower-cased)")
        
    # Genres cleaning
    if 'genres' in df.columns:
        df['genres'] = df['genres'].str.strip().str.capitalize()
        logging.info("Cleaned 'genres' column")

    return df

def regex_clean(df):
    """Uses regex to detect and clean complex text patterns."""
    logging.info("Starting regex cleaning...")
    
    # Example: Ensure 'key' follows the '/works/OL...' pattern
    if 'key' in df.columns:
        valid_key_pattern = re.compile(r'^/works/OL\d+W$')
        invalid_keys = df[~df['key'].str.match(valid_key_pattern, na=False)]
        if not invalid_keys.empty:
            logging.warning(f"Found {len(invalid_keys)} invalid keys")
            
    # Clean 'overview' - remove any HTML-like tags if present
    if 'overview' in df.columns:
        df['overview'] = df['overview'].str.replace(r'<[^>]*>', '', regex=True)
        logging.info("Cleaned 'overview' column using regex (removed HTML tags)")

    return df
