import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analytics.data_loader import get_mongo_data
from cleaning.missing_handler import handle_missing_values
from cleaning.string_cleaner import clean_strings, regex_clean
from cleaning.deduplicator import remove_duplicates
from cleaning.type_converter import convert_types
from cleaning.validator import validate_data

# Configure logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_cleaning_pipeline():
    """Implementation of the full cleaning workflow."""
    logging.info("========== Cleaning Pipeline Started ==========")
    
    # 1. Load Data
    df = get_mongo_data()
    
    # Map columns to match "movie dataset" requirements if necessary (for consistency with previous tasks)
    df = df.rename(columns={
        'subject': 'genres',
        'subtitle': 'overview',
        'ratings_average': 'rating'
    })
    
    # 2. Deduplication
    df = remove_duplicates(df)
    
    # 3. String Cleaning
    df = clean_strings(df)
    
    # 4. Regex Cleaning
    df = regex_clean(df)
    
    # 5. Missing Value Handling
    df = handle_missing_values(df)
    
    # 6. Type Conversion
    df = convert_types(df)
    
    # 7. Validation
    validate_data(df)
    
    # 8. Save cleaned data
    os.makedirs("data/processed/cleaned", exist_ok=True)
    cleaned_path = "data/processed/cleaned/cleaned_books.csv"
    df.to_csv(cleaned_path, index=False)
    
    logging.info(f"Cleaned data saved to {cleaned_path}")
    logging.info("========== Cleaning Pipeline Finished ==========")
    print(f"Cleaning complete. Results saved to {cleaned_path}")
    return df

if __name__ == "__main__":
    run_cleaning_pipeline()
