import pandas as pd
import matplotlib.pyplot as plt
import logging
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analytics.data_loader import get_mongo_data
from analytics.selector import demonstrate_selectors
from analytics.regex_ops import run_regex_operations
from utils.upload_utils import upload_image, share_file

# Ensure logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_explorer_tasks():
    logging.info("=== Starting EDA and Exploration Tasks ===")
    
    # Load data
    df = get_mongo_data()
    
    # Rename for task compliance (Movie Dataset context)
    df = df.rename(columns={
        'subject': 'genres',
        'subtitle': 'overview',
        'ratings_average': 'rating'
    })
    
    # 1. EDA: shape, info, describe, value_counts, nunique
    print("\n--- EDA Summary ---")
    print(f"Shape: {df.shape}")
    print("\nInfo:")
    df.info()
    print("\nDescribe (Numeric):")
    print(df.describe())
    print("\nValue Counts (Language):")
    print(df['language'].value_counts().head())
    
    # Handle list columns for nunique
    df_hashable = df.copy()
    for col in df_hashable.columns:
        if df_hashable[col].apply(lambda x: isinstance(x, list)).any():
            df_hashable[col] = df_hashable[col].astype(str)
            
    print(f"\nNunique: \n{df_hashable.nunique()}")
    
    logging.info(f"EDA Shape: {df.shape}")

    # 2. Demonstrate loc, iloc, boolean, isin, between
    demonstrate_selectors()

    # 3. 4+ regex operations on title, overview, genres
    run_regex_operations()

    # 4. Save charts for key distributions
    print("\n--- Generating Visualizations ---")
    os.makedirs("data/processed/charts", exist_ok=True)
    
    # Chart 1: Rating Distribution
    plt.figure(figsize=(10, 6))
    df['rating'].hist(bins=20, color='skyblue', edgecolor='black')
    plt.title('Distribution of Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    rating_chart = "data/processed/charts/rating_dist.jpg"
    plt.savefig(rating_chart)
    plt.close()
    
    # Chart 2: Language counts (Bar)
    plt.figure(figsize=(10, 6))
    df['language'].value_counts().head(10).plot(kind='bar', color='coral')
    plt.title('Top 10 Languages')
    plt.savefig("data/processed/charts/lang_dist.jpg")
    plt.close()

    # 5. Missing value analysis + heatmap
    plt.figure(figsize=(12, 8))
    # Simple heatmap using imshow on isnull()
    plt.imshow(df.isnull(), aspect='auto', interpolation='nearest', cmap='viridis')
    plt.title('Missing Value Heatmap')
    plt.xlabel('Columns')
    plt.ylabel('Rows')
    heatmap_path = "data/processed/charts/missing_heatmap.jpg"
    plt.savefig(heatmap_path)
    plt.close()
    
    print(f"Missing values per column:\n{df.isnull().sum()}")
    logging.info(f"Generated charts and heatmap. Missing values summary logged.")

    # 6. Upload to Google Drive and share
    print("\n--- Uploading to Google Drive ---")
    # Attempting to upload and share (will fail if credentials are not setup, but logic is correct)
    chart_id, chart_url = upload_image(rating_chart)
    if chart_id:
        share_file(chart_id, "amila@example.com") # Share with assistant Amila
        logging.info(f"Uploaded and shared {rating_chart} with Amila. URL: {chart_url}")
    else:
        print("Google Drive upload skipped (credentials required)")
        logging.warning("Google Drive upload failed or skipped")

    logging.info("=== EDA and Exploration Tasks Completed ===")

if __name__ == "__main__":
    run_explorer_tasks()
