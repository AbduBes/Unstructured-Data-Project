import sys
import os
import pandas as pd
import sqlite3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from utils.logger import logging
from storage.mongo import save_to_mongo
from api.client import fetch_books
from parsing.parsers import extract_book_fields
from parsing.pdf_parser import process_all_pdfs
from parsing.word_parser import process_all_word_docs
from parsing.excel_parser import process_all_excel_files
from cleaning.clean_pipeline import run_cleaning_pipeline
from analytics.data_combiner import merge_mysql_mongodb, demonstrate_join_types
from analytics.data_loader import get_aggregated_mongo_data
from analytics.aggregator import genre_summary, yearly_trends
from analytics.pivot_builder import build_pivot_table, wide_to_long
from analytics.time_series import parse_and_extract_dates, resample_yearly, compute_rolling_averages
from analytics.insight_reporter import (
    top_genres_by_rating, 
    engagement_ratio_by_genre, 
    yearly_publishing_trends, 
    language_distribution
)
from visualization.chart_generator import generate_all
from embeddings.chroma_store import get_client, get_or_create_collection, add_books, get_collection_info
from embeddings.embedder import load_model, generate_embeddings, combine_book_fields
from embeddings.similarity import multi_metric_search
import time

def run_embedding_demo(df: pd.DataFrame):
    """Demonstrates multi-metric search on the dataset."""
    logging.info("=== Starting Multi-Metric Search Demo ===")
    try:
        combined_text = combine_book_fields(df)
        texts = combined_text.tolist()
        
        # Load existing embeddings if available
        embedding_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'embeddings'))
        embedding_file = os.path.join(embedding_path, 'book_embeddings.npy')
        
        if os.path.exists(embedding_file):
            embeddings = np.load(embedding_file)
            query = "A high-stakes science fiction adventure set in a distant galaxy"
            multi_metric_search(query, texts, embeddings, top_n=5)
        else:
            logging.warning("Embeddings file not found. Skipping demo.")
            
    except Exception as e:
        logging.error(f"Multi-metric search demo failed: {e}")

def run_embedding_pipeline(df: pd.DataFrame):
    """Embeds books into ChromaDB."""
    logging.info("=== Starting Embedding Pipeline ===")
    try:
        embedding_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'embeddings'))
        embedding_file = os.path.join(embedding_path, 'book_embeddings.npy')
        os.makedirs(embedding_path, exist_ok=True)
        
        client = get_client(path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embeddings', 'chroma_db')))
        collection = get_or_create_collection(client, name='books_collection', reset=False)
        info = get_collection_info(collection)
        
        if os.path.exists(embedding_file) and info['count'] == len(df):
            logging.info("Embeddings already exist, skipping generation")
        else:
            combined_text = combine_book_fields(df)
            start_time = time.time()
            embeddings = generate_embeddings(combined_text.tolist())
            duration = time.time() - start_time
            np.save(embedding_file, embeddings)
            
            logging.info(f"Generated {len(embeddings)} embeddings, shape {embeddings.shape}, time taken: {duration:.2f}s")
            
            add_books(collection, df, embeddings)
            final_info = get_collection_info(collection)
            logging.info(f"Final collection count: {final_info['count']}")
            
    except Exception as e:
        logging.error(f"Embedding pipeline failed: {e}", exc_info=True)
        # Continue so other steps are not broken

def run_lab10_analytics():
    """Execute the full Lab 10 analytics pipeline."""
    logging.info("=== Starting Lab 10 Analytics Pipeline ===")
    try:
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'cleaned', 'cleaned_books.csv'))
        analytics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'analytics'))
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'outputs'))
        
        if not os.path.exists(csv_path):
            logging.info("Cleaned data not found. Running cleaning pipeline first.")
            run_cleaning_pipeline()
        
        df = pd.read_csv(csv_path)
        logging.info(f"Loaded {len(df)} rows from cleaned data.")
        
        # 1. MongoDB Aggregation Pipeline (4-stage)
        agg_mongo_df = get_aggregated_mongo_data()
        print("\n--- MongoDB Aggregation Result (Top Languages) ---")
        print(agg_mongo_df.head())
        
        # 2. MySQL simulation
        conn = sqlite3.connect(':memory:')
        df.to_sql('books', conn, index=False)
        mysql_df = pd.read_sql_query("""
            SELECT key, title, rating, ratings_count, edition_count, number_of_pages_median, has_fulltext 
            FROM books 
            WHERE rating > 0 AND ratings_count > 0
        """, conn)
        conn.close()
        
        # 3. Data Reshaping (Melt)
        melted_df = wide_to_long(
            mysql_df, 
            id_cols=['key', 'title'], 
            value_cols=['rating', 'ratings_count', 'number_of_pages_median']
        )
        logging.info(f"Melted DataFrame shape: {melted_df.shape}")
        
        # 4. Time Series Analysis
        # Ensure first_publish_year is in df
        df_ts = df.dropna(subset=['first_publish_year']).copy()
        df_ts = parse_and_extract_dates(df_ts)
        yearly_books = resample_yearly(df_ts)
        df_ts = compute_rolling_averages(df_ts, value_col='rating', windows=[3, 5])
        print("\n--- Time Series Analysis (Rolling Averages) ---")
        print(df_ts[['title', 'publish_date', 'rolling_avg_3', 'rolling_avg_5']].tail())

        # MongoDB simulation for joins
        mongo_df = df[['key', 'title', 'author_name', 'publisher', 'genres', 'language', 'first_publish_year', 'overview']].copy()
        
        # Demonstrate joins
        demonstrate_join_types(mysql_df, mongo_df)
        
        # Merge
        merged_df = merge_mysql_mongodb(mysql_df, mongo_df, on='key', how='inner')
        rename_cols = {
            'genres_mysql': 'genres', 
            'title_mysql': 'title', 
            'rating_mysql': 'rating', 
            'ratings_count_mysql': 'ratings_count',
            'first_publish_year_mysql': 'first_publish_year',
            'number_of_pages_median_mysql': 'number_of_pages_median',
            'author_name_mysql': 'author_name'
        }
        merged_df = merged_df.rename(columns=rename_cols)
        
        # Ensure dirs exist
        os.makedirs(analytics_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Analytics & Reporting
        top_genres_by_rating(merged_df)
        engagement_ratio_by_genre(merged_df)
        yearly_publishing_trends(merged_df, start=1900, end=2024)
        language_distribution(merged_df)
        
        logging.info("=== Lab 10 Analytics Pipeline Finished ===")
    except Exception as e:
        logging.error(f"Lab 10 pipeline failed: {e}", exc_info=True)
        raise



def run_api_pipeline():
    """Fetch books from Open Library API and store in MongoDB."""
    logging.info("=== Starting API Pipeline ===")

    # Just 1 page for this test!
    books = fetch_books(query="dune", pages=1)

    for book_page in books:
        docs = book_page["data"].get("docs", [])
        
        # --- NEW DEBUGGING BLOCK ---
        if docs:
            print("\n" + "="*50)
            print("RAW DATA RECEIVED FOR THE FIRST BOOK:")
            print(f"Title: {docs[0].get('title')}")
            print(f"Raw Ratings Average: {docs[0].get('ratings_average')}")
            print("="*50 + "\n")
        # ---------------------------
        
        for book in docs:
            parsed = extract_book_fields(book)
            save_to_mongo(parsed, "openlibrary_api")

    logging.info("API pipeline completed successfully")


def run_document_pipeline():
    """Extract and store data from local PDF, Word, and Excel files."""
    logging.info("=== Starting Document Extraction Pipeline ===")

    # Resolve data folder relative to project root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    pdf_folder   = os.path.join(base_dir, "data", "raw", "pdf")
    word_folder  = os.path.join(base_dir, "data", "raw", "word")
    excel_folder = os.path.join(base_dir, "data", "raw", "excel")

    logging.info("Processing PDF files...")
    process_all_pdfs(pdf_folder)

    logging.info("Processing Word documents...")
    process_all_word_docs(word_folder)

    logging.info("Processing Excel files...")
    process_all_excel_files(excel_folder)

    logging.info("Document extraction pipeline completed successfully")


import numpy as np
import time

# ... [imports] ...
# [previous functions]

def run_visualizations_pipeline():
    """Generate all static and interactive charts for the book dataset."""
    logging.info("=== Starting Visualization Pipeline ===")
    try:
        generate_all()
        logging.info("Visualization pipeline completed successfully")
    except Exception as e:
        logging.error(f"Visualization pipeline failed: {e}", exc_info=True)


def run_pipeline():
    """Orchestrate the full pipeline: API + document extraction + Lab 10 analytics + Visualizations."""
    logging.info("========== Pipeline Started ==========")

    run_api_pipeline()
    #run_document_pipeline()
    run_lab10_analytics()
    
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'cleaned', 'cleaned_books.csv'))
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        run_embedding_pipeline(df)
        run_embedding_demo(df)
    
    # New visualization step
    run_visualizations_pipeline()

    logging.info("========== Pipeline Finished ==========")


if __name__ == "__main__":
    run_pipeline()