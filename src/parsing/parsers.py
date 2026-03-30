import csv
import xml.etree.ElementTree as ET
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from storage.mongo import save_to_mongo 

def extract_book_fields(book):
    # author_name is a list in Open Library API (e.g. ["J. K. Rowling"])
    author = book.get("author_name")
    if isinstance(author, list):
        author = ", ".join(author)

    return {
        "id": book.get("key") or book.get("id"),           # /works/OL82563W
        "title": book.get("title"),
        "author": author,
        "published_year": book.get("first_publish_year")    # mapped from first_publish_year
                          or book.get("published_year"),
    }

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

if __name__ == "__main__":
    parse_json_files()
    # parse_csv_file("../../data/raw/csv/sample.csv")
    # parse_xml_file("../../data/raw/xml/sample.xml")