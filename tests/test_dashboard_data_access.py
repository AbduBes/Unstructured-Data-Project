"""Unit tests for the dashboard's data-normalising and filtering helpers.

These run against small in-memory DataFrames, so no MongoDB or CSV is needed.
"""
import numpy as np
import pandas as pd
import pytest

from dashboard.data_access import (
    _normalise,
    filter_books,
    get_genres,
    get_year_bounds,
)


@pytest.fixture
def books():
    return _normalise(pd.DataFrame({
        "_id": [1, 2, 3, 4, 5],
        "title": ["Dune", "Dune Messiah", None, "Gödel, Escher, Bach", "No Year"],
        "genres": ["Science fiction", "Science fiction", "  ", None, "Fiction"],
        "first_publish_year": ["1965", 1969, 1976, 1979, None],
        "rating": ["4.30", "3.95", "bad", 4.4, 3.0],
        "ratings_count": [414, 132, 42, 60, 1],
    }))


def test_normalise_drops_mongo_id(books):
    assert "_id" not in books.columns


def test_normalise_drops_rows_without_a_year(books):
    assert "No Year" not in books["title"].tolist()
    assert len(books) == 4
    assert books["first_publish_year"].dtype.kind == "i"


def test_normalise_coerces_bad_numbers_to_nan(books):
    assert books.loc[0, "rating"] == pytest.approx(4.30)
    assert np.isnan(books.loc[2, "rating"])


def test_normalise_fills_missing_titles_and_genres(books):
    assert books.loc[2, "title"] == "Untitled"
    assert books.loc[2, "genres"] == "Unknown"   # blank string
    assert books.loc[3, "genres"] == "Unknown"   # missing value


def test_get_genres_is_sorted_and_unique(books):
    assert get_genres(books) == ["Science fiction", "Unknown"]


def test_get_year_bounds(books):
    assert get_year_bounds(books) == (1965, 1979)


def test_get_year_bounds_defaults_for_empty_data():
    assert get_year_bounds(pd.DataFrame({"first_publish_year": []})) == (1900, 2025)


def test_filter_by_genre(books):
    out = filter_books(books, genre="Science fiction")
    assert out["title"].tolist() == ["Dune", "Dune Messiah"]


def test_filter_by_year_range_is_inclusive(books):
    out = filter_books(books, year_range=[1969, 1976])
    assert out["first_publish_year"].tolist() == [1969, 1976]


def test_filter_by_search_is_case_insensitive(books):
    out = filter_books(books, search="  dUNE ")
    assert out["title"].tolist() == ["Dune", "Dune Messiah"]


def test_filters_combine(books):
    out = filter_books(books, genre="Science fiction", year_range=[1960, 1966], search="dune")
    assert out["title"].tolist() == ["Dune"]


def test_no_filters_returns_everything(books):
    assert len(filter_books(books)) == len(books)
