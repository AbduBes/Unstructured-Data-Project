"""Data access layer for the Lab 13 dashboard.

All database logic lives here so the layout and callbacks stay simple and
testable. The dashboard's primary data source is **MongoDB**; if MongoDB is
unavailable (e.g. the container isn't running, or the collection hasn't been
seeded yet) we fall back **gracefully** to the cleaned CSV produced by the
earlier cleaning lab. Either way the rest of the app receives one tidy,
type-normalised :class:`pandas.DataFrame` of book records.

The module also exposes small helpers the layout and callbacks reuse:

* :func:`get_genres`     - sorted list of genres for the dropdown.
* :func:`get_year_bounds`- (min_year, max_year) for the range slider.
* :func:`filter_books`   - slice the dataset by genre, year range and search text.

Configuration is read from environment variables so the same code works on a
laptop and inside Docker Compose (where Mongo is reachable as host ``db``):

    MONGO_URI        default "mongodb://localhost:27017/"
    MONGO_DB         default "book_pipeline"
    MONGO_COLLECTION default "books"
    CLEAN_CSV_PATH   default <project>/data/processed/cleaned/cleaned_books.csv
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuration (all overridable via environment variables)
# --------------------------------------------------------------------------- #
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.environ.get("MONGO_DB", "book_pipeline")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "books")

# Project root is two levels up from this file: src/dashboard/data_access.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_FALLBACK = Path(
    os.environ.get(
        "CLEAN_CSV_PATH",
        str(PROJECT_ROOT / "data" / "processed" / "cleaned" / "cleaned_books.csv"),
    )
)

# How long to wait for MongoDB before giving up and using the CSV fallback.
MONGO_TIMEOUT_MS = int(os.environ.get("MONGO_TIMEOUT_MS", "3000"))

# Columns the dashboard treats as numeric. Anything non-numeric becomes NaN.
NUMERIC_COLS: Sequence[str] = (
    "first_publish_year",
    "rating",
    "ratings_count",
    "number_of_pages_median",
    "edition_count",
)

# Module-level cache so callbacks don't re-query the database on every event.
_CACHE: Optional[pd.DataFrame] = None
_SOURCE: str = "unknown"


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce types and drop rows the charts can't use.

    Keeps the dashboard robust regardless of whether the rows came from
    MongoDB (typed loosely) or a freshly parsed CSV.
    """
    df = df.copy()

    # Mongo's internal id is never useful to the UI.
    df.drop(columns=[c for c in ("_id",) if c in df.columns], inplace=True)

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "genres" in df.columns:
        df["genres"] = df["genres"].fillna("Unknown").astype(str).str.strip()
        df.loc[df["genres"] == "", "genres"] = "Unknown"

    if "title" in df.columns:
        df["title"] = df["title"].fillna("Untitled").astype(str)

    # A valid publication year is required by the year slider / trend chart.
    if "first_publish_year" in df.columns:
        df = df[df["first_publish_year"].notna()]
        df["first_publish_year"] = df["first_publish_year"].astype(int)

    return df.reset_index(drop=True)


def load_from_mongo() -> pd.DataFrame:
    """Load the books collection from MongoDB.

    Raises on any connection / emptiness problem so the caller can fall back
    to CSV. We import :mod:`pymongo` lazily so the module still imports even
    in an environment where pymongo isn't installed.
    """
    from pymongo import MongoClient  # local import keeps the module importable

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIMEOUT_MS)
    # Force an actual round-trip; this raises quickly if Mongo is unreachable.
    client.admin.command("ping")

    collection = client[MONGO_DB][MONGO_COLLECTION]
    docs = list(collection.find({}, {"_id": 0}))
    if not docs:
        raise ValueError(
            f"MongoDB collection '{MONGO_DB}.{MONGO_COLLECTION}' is empty - "
            f"run scripts/seed_mongo.py first."
        )

    logger.info("Loaded %d documents from MongoDB (%s.%s)",
                len(docs), MONGO_DB, MONGO_COLLECTION)
    return pd.DataFrame(docs)


def load_from_csv() -> pd.DataFrame:
    """Load the cleaned book dataset from the CSV fallback."""
    if not CSV_FALLBACK.exists():
        raise FileNotFoundError(f"CSV fallback not found at {CSV_FALLBACK}")
    logger.info("Loaded book data from CSV fallback: %s", CSV_FALLBACK)
    return pd.read_csv(CSV_FALLBACK, low_memory=False)


def load_data(force_reload: bool = False) -> pd.DataFrame:
    """Return the book dataset, trying MongoDB first then the CSV fallback.

    The result is cached at module level so repeated callback invocations are
    cheap. Pass ``force_reload=True`` to re-query (e.g. after re-seeding).
    """
    global _CACHE, _SOURCE
    if _CACHE is not None and not force_reload:
        return _CACHE

    try:
        df = load_from_mongo()
        _SOURCE = "mongodb"
    except Exception as exc:  # broad on purpose: ANY failure -> CSV fallback
        logger.warning("MongoDB unavailable (%s). Falling back to CSV.", exc)
        df = load_from_csv()
        _SOURCE = "csv"

    _CACHE = _normalise(df)
    logger.info("Dashboard dataset ready: %d rows from %s", len(_CACHE), _SOURCE)
    return _CACHE


def get_source() -> str:
    """Return where the cached data came from: 'mongodb', 'csv' or 'unknown'."""
    return _SOURCE


# --------------------------------------------------------------------------- #
# Helpers for the UI
# --------------------------------------------------------------------------- #
def get_genres(df: Optional[pd.DataFrame] = None) -> list[str]:
    """Return the sorted list of distinct genres for the dropdown filter."""
    df = load_data() if df is None else df
    if "genres" not in df.columns:
        return []
    return sorted(g for g in df["genres"].dropna().unique() if str(g).strip())


def get_year_bounds(df: Optional[pd.DataFrame] = None) -> tuple[int, int]:
    """Return ``(min_year, max_year)`` for the range slider."""
    df = load_data() if df is None else df
    if "first_publish_year" not in df.columns or df.empty:
        return (1900, 2025)
    years = df["first_publish_year"].dropna()
    if years.empty:
        return (1900, 2025)
    return int(years.min()), int(years.max())


def filter_books(
    df: Optional[pd.DataFrame] = None,
    genre: Optional[str] = None,
    year_range: Optional[Sequence[int]] = None,
    search: Optional[str] = None,
) -> pd.DataFrame:
    """Filter the dataset by genre, year range and/or title search text.

    Every argument is optional; ``None`` (or empty) means "don't filter on
    this field". Callbacks pass the current value of each UI control here.
    """
    out = load_data() if df is None else df

    if genre:
        out = out[out["genres"] == genre]

    if year_range and "first_publish_year" in out.columns:
        low, high = year_range[0], year_range[1]
        out = out[
            (out["first_publish_year"] >= low) & (out["first_publish_year"] <= high)
        ]

    if search and "title" in out.columns:
        out = out[out["title"].str.contains(str(search).strip(), case=False, na=False)]

    return out
