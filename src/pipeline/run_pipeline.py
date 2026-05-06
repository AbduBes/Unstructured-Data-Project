import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from utils.logger import logging
from storage.mongo import save_to_mongo
from api.client import fetch_books
from parsing.parsers import extract_book_fields
from parsing.pdf_parser import process_all_pdfs
from parsing.word_parser import process_all_word_docs
from parsing.excel_parser import process_all_excel_files


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


def run_pipeline():
    """Orchestrate the full pipeline: API + document extraction."""
    logging.info("========== Pipeline Started ==========")

    run_api_pipeline()
    #run_document_pipeline()

    logging.info("========== Pipeline Finished ==========")


if __name__ == "__main__":
    run_pipeline()