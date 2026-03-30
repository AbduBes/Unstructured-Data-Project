from pymongo import MongoClient
from datetime import datetime
import logging

client = MongoClient("mongodb://localhost:27017/")
db = client["book_pipeline"]
collection = db["raw_books"]


def save_to_mongo(data, source_url):
    """
    Save extracted content to MongoDB with full metadata.

    Supports two modes:
    - Legacy (API/parser): data is a plain dict of book fields.
      Metadata is generated automatically.
    - Document extraction (PDF/Word/Excel): data already contains
      'content' and 'metadata' keys — stored as-is with a version stamp.
    """
    try:
        # Document extraction mode: data already has content + metadata
        if isinstance(data, dict) and "content" in data and "metadata" in data:
            document = {
                "content": data["content"],
                "metadata": {
                    **data["metadata"],
                    "fetched_at": datetime.utcnow(),  # pipeline insertion time
                    "version": 1
                },
                "source": source_url
            }
        else:
            # Legacy API/parser mode: wrap raw data with basic metadata
            document = {
                "data": data,
                "metadata": {
                    "file_name": None,
                    "document_type": "api",
                    "extraction_timestamp": datetime.utcnow(),
                    "source": source_url,
                    "extraction_library": None
                },
                "source": source_url,
                "fetched_at": datetime.utcnow(),
                "version": 1
            }

        result = collection.insert_one(document)
        logging.info(f"Inserted document with id {result.inserted_id} from source: {source_url}")

    except Exception as e:
        logging.error(f"Failed to save document to MongoDB: {e}")