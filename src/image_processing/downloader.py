import requests
import os
import time
import logging
from pathlib import Path

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_book_cover_url(cover_id, size="L"):
    
    return f"https://covers.openlibrary.org/b/id/{cover_id}-{size}.jpg"


def download_book_covers(books_data, save_dir="data/raw/images", max_books=10):
    
    os.makedirs(save_dir, exist_ok=True)
    downloaded_files = []
    
    count = 0
    for book in books_data:
        if count >= max_books:
            break
            
        # Get cover_i from the book data (this is cover ID in Open Library)
        cover_ids = book.get("cover_i") or book.get("cover_id")
        
        if not cover_ids:
            logging.warning(f"No cover found for book: {book.get('title', 'Unknown')}")
            continue
        
        # Handle both single cover_id and list of cover_ids
        if isinstance(cover_ids, list):
            cover_id = cover_ids[0]
        else:
            cover_id = cover_ids
            
        title = book.get("title", "unknown").replace("/", "_").replace("\\", "_")
        book_key = book.get("key", "").replace("/works/", "")
        
        filename = f"{book_key}_{title[:30]}.jpg"
        filepath = os.path.join(save_dir, filename)
        
        # Download the cover
        cover_url = get_book_cover_url(cover_id, size="L")
        
        try:
            response = requests.get(cover_url, timeout=10)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            logging.info(f"Downloaded cover: {filename}")
            downloaded_files.append(filepath)
            count += 1
            
            # Be nice to the API
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download {cover_url}: {e}")
            continue
    
    logging.info(f"Successfully downloaded {len(downloaded_files)} book covers")
    return downloaded_files


def fetch_and_download_covers(query="python programming", num_books=10):
    
    # Search for books
    search_url = "https://openlibrary.org/search.json"
    params = {
        "q": query,
        "limit": num_books * 2,  # Request more to account for missing covers
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        books = data.get("docs", [])
        logging.info(f"Found {len(books)} books for query: {query}")
        
        # Download covers
        return download_book_covers(books, max_books=num_books)
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching books from Open Library: {e}")
        return []


if __name__ == "__main__":
    # Test the downloader
    print("Downloading book covers from Open Library...")
    files = fetch_and_download_covers(query="classic literature", num_books=5)
    print(f"Downloaded {len(files)} covers:")
    for f in files:
        print(f"  - {f}")