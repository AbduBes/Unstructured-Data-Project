"""Unit tests for mapping raw Open Library API records to flat book rows."""
from parsing.parsers import extract_book_fields


def test_list_fields_are_flattened_to_first_value():
    record = {
        "key": "/works/OL893415W",
        "title": "Dune",
        "author_name": ["Frank Herbert", "Someone Else"],
        "publisher": ["Penguin Classics", "Ace"],
        "language": ["eng", "fre"],
        "subject": ["Science fiction", "Desert"],
        "edition_key": ["OL28969075M", "OL1M"],
    }
    row = extract_book_fields(record)

    assert row["key"] == "/works/OL893415W"
    assert row["title"] == "Dune"
    assert row["author_name"] == "Frank Herbert"
    assert row["publisher"] == "Penguin Classics"
    assert row["language"] == "eng"
    assert row["subject"] == "Science fiction"
    assert row["edition_key"] == "OL28969075M"


def test_scalar_fields_are_kept_as_is():
    row = extract_book_fields({"author_name": "Frank Herbert", "publisher": "Ace"})
    assert row["author_name"] == "Frank Herbert"
    assert row["publisher"] == "Ace"


def test_missing_fields_become_none_without_raising():
    row = extract_book_fields({})

    assert row["title"] is None
    assert row["author_name"] is None
    assert row["ratings_average"] is None
    assert row["subject_facet"] == []


def test_numeric_fields_are_passed_through():
    record = {
        "first_publish_year": 1965,
        "edition_count": 120,
        "number_of_pages_median": 592,
        "ratings_average": 4.3,
        "ratings_count": 414,
        "has_fulltext": True,
    }
    row = extract_book_fields(record)

    assert row["first_publish_year"] == 1965
    assert row["edition_count"] == 120
    assert row["number_of_pages_median"] == 592
    assert row["ratings_average"] == 4.3
    assert row["ratings_count"] == 414
    assert row["has_fulltext"] is True


def test_output_has_a_stable_schema():
    expected = {
        "key", "edition_key", "title", "subtitle", "author_name", "publisher",
        "subject", "subject_facet", "language", "first_publish_year",
        "edition_count", "number_of_pages_median", "ratings_average",
        "ratings_count", "has_fulltext",
    }
    assert set(extract_book_fields({"title": "x"})) == expected
