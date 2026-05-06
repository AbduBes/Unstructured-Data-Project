import requests
import os
import time
#from dotenv import load_dotenv
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from utils.logger import logging

#load_dotenv()

url = "https://openlibrary.org/search.json"

def fetch_books(query="dune", pages=1):
    all_books = []
    
    # Notice this is a single STRING, not a list []
    # These are the exact fields you used in your successful browser test
# Added publisher, subject, number_of_pages_median, and subtitle to the list!
    target_fields_string = "key,edition_key,title,author_name,language,first_publish_year,edition_count,ratings_average,ratings_count,publisher,subject,subject_facet,number_of_pages_median,subtitle,has_fulltext"
    for page in range(1, pages + 1):
        params = {
            "q": query,
            "page": page,
            "fields": target_fields_string  # Pass the explicit string here!
        }
        
        response = safe_request(url, params)

        if response:
            data = response.json()
            all_books.append({
                "page": page,
                "data": data
            })
        else:
            print(f"Error occurred on page {page}. Skipping.")
            continue

    return all_books

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
    
    # Introduce our script properly to unlock full API features
    headers = {
        "User-Agent": "UnstructuredDataProject/1.0 (contact@example.com)"
    }

    for i in range(retries):
        try:
            # Pass the headers into the get request
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            logging.info(f"Successfully fetched data from {url} (Page {params.get('page')})")

            return response

        except requests.exceptions.RequestException as e:
            logging.error(f"Error on attempt {i + 1}: {e}")

            if response is not None:
                logging.error(f"Response: {response.text}")

            time.sleep(2 ** i)

    logging.error(f"Failed after {retries} attempts.")
    return None

if __name__ == "__main__":
    books = fetch_books(query="Dune", pages=3)

    for book_page in books:
        save_raw_data(book_page["data"], book_page["page"])