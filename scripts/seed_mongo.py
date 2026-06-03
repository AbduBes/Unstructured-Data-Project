"""One-time MongoDB seeding script for the Lab 13 dashboard.

Reads the cleaned book dataset from ``data/processed/cleaned/`` and loads it
into MongoDB so the dashboard can query the database instead of the CSV. In a
real production setup the pipeline would populate Mongo; for local development
this script gives you a quick, repeatable way to (re)fill the collection.

What it does:
    1. Read the cleaned CSV into a DataFrame.
    2. Connect to MongoDB (defaults / environment variables).
    3. Drop the existing collection so re-seeding is idempotent.
    4. Insert every book record.
    5. Create indexes on genres, first_publish_year and title for fast filtering.

Usage:
    python scripts/seed_mongo.py
    # or, against a custom server:
    MONGO_URI="mongodb://localhost:27017/" python scripts/seed_mongo.py
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import pandas as pd
from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("seed_mongo")

# --------------------------------------------------------------------------- #
# Configuration (overridable via environment variables)
# --------------------------------------------------------------------------- #
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.environ.get("MONGO_DB", "book_pipeline")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "books")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = Path(
    os.environ.get(
        "CLEAN_CSV_PATH",
        str(PROJECT_ROOT / "data" / "processed" / "cleaned" / "cleaned_books.csv"),
    )
)


def load_records(csv_path: Path) -> list[dict]:
    """Read the cleaned CSV and return a list of MongoDB-ready dicts."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {csv_path}")

    df = pd.read_csv(csv_path, low_memory=False)
    logger.info("Read %d rows from %s", len(df), csv_path)

    # Drop the CSV's pre-existing string id so Mongo assigns fresh ObjectIds.
    df = df.drop(columns=[c for c in ("_id",) if c in df.columns])

    # NaN -> None so the documents are clean JSON-like records.
    return df.where(pd.notnull(df), None).to_dict("records")


def seed(uri: str = MONGO_URI, db_name: str = MONGO_DB,
         collection_name: str = MONGO_COLLECTION) -> int:
    """Seed the collection. Returns the number of inserted documents."""
    records = load_records(CSV_PATH)
    if not records:
        logger.warning("No records to insert; aborting.")
        return 0

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")  # fail fast if Mongo is unreachable
    collection = client[db_name][collection_name]

    # Idempotent: clear then re-insert.
    collection.drop()
    result = collection.insert_many(records)
    inserted = len(result.inserted_ids)
    logger.info("Inserted %d documents into %s.%s",
                inserted, db_name, collection_name)

    # Indexes speed up the dashboard's genre/year/title filtering.
    collection.create_index([("genres", ASCENDING)])
    collection.create_index([("first_publish_year", ASCENDING)])
    collection.create_index([("title", ASCENDING)])
    logger.info("Created indexes on genres, first_publish_year, title")

    client.close()
    return inserted


def main() -> int:
    logger.info("Seeding MongoDB at %s -> %s.%s",
                MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    try:
        inserted = seed()
        logger.info("Done. %d documents are ready for the dashboard.", inserted)
        return 0
    except FileNotFoundError as exc:
        logger.error("%s", exc)
    except PyMongoError as exc:
        logger.error("MongoDB error: %s", exc)
        logger.error("Is MongoDB running? Try: docker compose up -d db")
    except Exception as exc:  # noqa: BLE001 - report anything else clearly
        logger.error("Unexpected error: %s", exc)
    return 1


if __name__ == "__main__":
    sys.exit(main())
