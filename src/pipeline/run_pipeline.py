import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))


from utils.logger import logging 
from storage.mongo import save_to_mongo
from api.client import fetch_movies
from parsing.parsers import extract_book_fields


def run_pipeline():
   books = fetch_books(3)


   for book in books:
       parsed = extract_book_fields(book)


       save_to_mongo(parsed, "tmdb_api")


   logging.info("Pipeline finished successfully")


if __name__ == "__main__":
   run_pipeline()