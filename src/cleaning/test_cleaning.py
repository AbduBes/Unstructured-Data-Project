import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cleaning.string_cleaner import clean_strings
from cleaning.missing_handler import handle_missing_values
from cleaning.deduplicator import remove_duplicates
from cleaning.type_converter import convert_types

def test_string_cleaning():
    df = pd.DataFrame({'title': ['  dune  ', 'MESSIAH'], 'language': [' ENG ', 'fre']})
    cleaned = clean_strings(df)
    assert cleaned['title'].iloc[0] == 'Dune'
    assert cleaned['title'].iloc[1] == 'Messiah'
    assert cleaned['language'].iloc[0] == 'eng'

def test_missing_handler():
    df = pd.DataFrame({
        'title': ['Book1', 'Book2'],
        'rating': [4.5, np.nan],
        'language': [np.nan, 'eng']
    })
    cleaned = handle_missing_values(df)
    assert cleaned['language'].iloc[0] == 'Unknown'
    assert cleaned['rating'].iloc[1] == 4.5 # Median of 4.5 is 4.5

def test_deduplication():
    df = pd.DataFrame({
        'key': ['A', 'A', 'B'],
        'title': ['T1', 'T1', 'T2']
    })
    cleaned = remove_duplicates(df)
    assert len(cleaned) == 2

def test_type_conversion():
    df = pd.DataFrame({
        'first_publish_year': ['1965', '1969'],
        'rating': ['4.5', '3.8']
    })
    cleaned = convert_types(df)
    assert cleaned['first_publish_year'].dtype in [np.int64, np.float64, np.int32]
    assert cleaned['rating'].dtype in [np.float64, np.float32]

if __name__ == "__main__":
    pytest.main([__file__])
