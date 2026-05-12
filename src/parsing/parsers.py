import requests
import os
import time
from dotenv import load_dotenv
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from utils.logger import logging

#load_dotenv()

url = "https://openlibrary.org/search.json"

# Define the exact fields we want to fetch from the API
#TARGET_FIELDS = "key,edition_key,title,subtitle,author_name,publisher,subject,subject_facet,language,first_publish_year,edition_count,number_of_pages_median,ratings_average,ratings_count,has_fulltext"

def extract_book_fields(book):
    """
    Safely extract and map specific fields from an Open Library book API record 
    or a standard dictionary payload.
    """
    return {
        # Identifiers
        "key":                    book.get("key"),           
        "edition_key":            book.get("edition_key", [None])[0] if isinstance(book.get("edition_key"), list) else book.get("edition_key"),

        # Core text (title/overview/genre equivalents)
        "title":                  book.get("title"),
        "subtitle":               book.get("subtitle"),      
        "author_name":            book.get("author_name", [None])[0] if isinstance(book.get("author_name"), list) else book.get("author_name"),
        "publisher":              book.get("publisher", [None])[0] if isinstance(book.get("publisher"), list) else book.get("publisher"),

        # Genre/category proxy 
        "subject":                book.get("subject", [None])[0] if isinstance(book.get("subject"), list) else book.get("subject"),
        "subject_facet":          book.get("subject_facet", []),  

        # Language 
        "language":               book.get("language", [None])[0] if isinstance(book.get("language"), list) else book.get("language"),

        # Numeric 
        "first_publish_year":     book.get("first_publish_year"),
        "edition_count":          book.get("edition_count"),
        "number_of_pages_median": book.get("number_of_pages_median"),
        "ratings_average":        book.get("ratings_average"),    
        "ratings_count":          book.get("ratings_count"),
        
        # Boolean flags
        "has_fulltext":           book.get("has_fulltext"),
    }

def save_raw_data(data, page_num):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, "..", "..", "data", "raw", "api")
    os.makedirs(folder_path, exist_ok=True)

    filename = f"books_page_{page_num}.json"
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Raw data saved to {os.path.abspath(file_path)}")

def safe_request(url, params, retries=3):
    response = None

    for i in range(retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            logging.info(f"Successfully fetched data from {url} (Page {params['page']})")

            return response

        except requests.exceptions.RequestException as e:
            logging.error(f"Error on attempt {i + 1}: {e}")

            if response is not None:
                logging.error(f"Response: {response.text}")

            time.sleep(2 ** i)

    logging.error(f"Failed after {retries} attempts.")
    return None

if __name__ == "__main__":
    books = fetch_books(query="Dune", pages=1)

    for book_page in books:
        save_raw_data(book_page["data"], book_page["page"])


def parse_csv_file(file_path):
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)  
        for row in reader:
            # print(f"ID: {row['id']}, Title: {row['title']}, Release Date: {row['release_date']}, Popularity: {row['popularity']}")
            book_fields = extract_book_fields(row)  
            print(f"Saving to MongoDB: {book_fields}")
            save_to_mongo(book_fields, "CSV Source")
            

def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    for item in root.findall("book"):
        book = {
            "id": item.find("id").text,
            "title": item.find("title").text,
            "author_name": item.find("author_name").text,
            "published_year": item.find("published_year").text,
        }
        # print(f"ID: {book['id']}, Title: {book['title']}, Release Date: {book['release_date']}, Popularity: {book['popularity']}")
        book_fields = extract_book_fields(book) 
        print(f"Saving to MongoDB: {book_fields}")
        save_to_mongo(book_fields, "XML Source")

def parse_json_files():
    folder_path = "../../data/raw/api/"

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r") as f:
                data = json.load(f)

            # Handle Open Library API response format: {"docs": [...], "numFound": ...}
            if isinstance(data, dict) and "docs" in data:
                books = data["docs"]
            elif isinstance(data, dict):
                books = [data]  # single book object
            elif isinstance(data, list):
                books = data
            else:
                print(f"Unexpected structure in {filename}: {data}")
                continue

            for book in books:
                book_fields = extract_book_fields(book)
                print(f"Saving to MongoDB: {book_fields}")
                save_to_mongo(book_fields, filename)