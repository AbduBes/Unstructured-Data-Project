import pandas as pd
import numpy as np
from pymongo import MongoClient
import logging
import os

# Ensure logging is configured
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_mongo_data():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["book_pipeline"]
    collection = db["raw_books"]
    
    data = list(collection.find())
    logging.info(f"Loaded {len(data)} documents from MongoDB")
    
    # Flattening nested data
    flattened = []
    for doc in data:
        row = doc.get('data', {})
        row['_id'] = str(doc.get('_id'))
        flattened.append(row)
        
    df = pd.DataFrame(flattened)
    return df

def optimize_dtypes(df):
    logging.info("Optimizing dtypes...")
    before_mem = df.memory_usage(deep=True).sum() / 1024**2
    
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = pd.to_numeric(df[col], downcast='float')
        elif df[col].dtype == 'int64':
            df[col] = pd.to_numeric(df[col], downcast='integer')
        elif df[col].dtype == 'object' and col == 'language':
            df[col] = df[col].astype('category')
            
    after_mem = df.memory_usage(deep=True).sum() / 1024**2
    logging.info(f"Memory Usage Before: {before_mem:.2f} MB, After: {after_mem:.2f} MB")
    print(f"Memory optimized: {before_mem:.2f} MB -> {after_mem:.2f} MB")
    return df

def run_data_tasks():
    logging.info("=== Starting Data Loading Tasks ===")
    
    # 1. Load from MongoDB
    df = get_mongo_data()
    
    # 2. Export raw CSV (and make it "large" by replicating)
    csv_path = "data/raw/large_dataset.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # Replicate 100 times to make it "large" for chunking demonstration
    large_df = pd.concat([df] * 100, ignore_index=True)
    large_df.to_csv(csv_path, index=False)
    logging.info(f"Exported replicated dataset to {csv_path} ({len(large_df)} rows)")

    # 3. Load large CSV in chunks; compute global mean of rating column
    chunk_size = 50
    rating_col = 'ratings_average'
    
    total_sum = 0
    total_count = 0
    
    logging.info(f"Processing {csv_path} in chunks of {chunk_size}")
    
    # 4. Process chunks per-language; combine accumulators
    lang_accumulators = {} # {lang: {'sum': 0, 'count': 0}}

    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        # Global mean accumulators
        valid_ratings = chunk[rating_col].dropna()
        total_sum += valid_ratings.sum()
        total_count += len(valid_ratings)
        
        # Per-language accumulators
        for lang, group in chunk.groupby('language'):
            if lang not in lang_accumulators:
                lang_accumulators[lang] = {'sum': 0, 'count': 0}
            
            group_ratings = group[rating_col].dropna()
            lang_accumulators[lang]['sum'] += group_ratings.sum()
            lang_accumulators[lang]['count'] += len(group_ratings)

    global_mean = total_sum / total_count if total_count > 0 else 0
    print(f"\nGlobal Mean Rating: {global_mean:.4f}")
    logging.info(f"Computed Global Mean Rating: {global_mean}")

    print("\nPer-Language Mean Ratings (from accumulators):")
    for lang, acc in lang_accumulators.items():
        lang_mean = acc['sum'] / acc['count'] if acc['count'] > 0 else 0
        print(f"Language: {lang}, Mean Rating: {lang_mean:.4f}")
        logging.info(f"Language: {lang}, Mean Rating: {lang_mean}")

    # 5. Optimise dtypes
    df_optimized = optimize_dtypes(df)
    
    logging.info("=== Data Loading Tasks Completed ===")

if __name__ == "__main__":
    run_data_tasks()
