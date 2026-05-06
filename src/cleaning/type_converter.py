import pandas as pd
import logging

def convert_types(df):
    """Converts columns into correct data types."""
    logging.info("Starting type conversion...")
    
    # Numeric conversions
    numeric_cols = ['first_publish_year', 'edition_count', 'number_of_pages_median', 'rating', 'ratings_count']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            logging.info(f"Converted '{col}' to numeric")

    # Categorical
    if 'language' in df.columns:
        df['language'] = df['language'].astype('category')
        logging.info("Converted 'language' to categorical")

    return df
