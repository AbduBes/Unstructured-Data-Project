import pandas as pd
import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analytics.data_loader import get_mongo_data

# Ensure logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def demonstrate_selectors():
    logging.info("=== Starting Pandas Selector Demonstrations ===")
    
    # Load data
    df = get_mongo_data()
    
    # Rename for task compliance (Movie Dataset context)
    df = df.rename(columns={
        'subject': 'genres',
        'subtitle': 'overview',
        'ratings_average': 'rating'
    })
    
    print("\n--- Pandas Indexing Demonstrations ---")
    
    # loc: Label based
    print("loc demo (first 2 rows, title and rating):")
    loc_res = df.loc[:1, ['title', 'rating']]
    print(loc_res)
    logging.info("Demonstrated .loc indexing")
    
    # iloc: Integer based
    print("\niloc demo (row 0, col 2):")
    iloc_res = df.iloc[0, 2]
    print(iloc_res)
    logging.info("Demonstrated .iloc indexing")
    
    # boolean indexing: Ratings > 4.0
    print("\nBoolean indexing (rating > 4.0):")
    high_rated = df[df['rating'] > 4.0]
    print(high_rated[['title', 'rating']].head())
    logging.info("Demonstrated boolean indexing")
    
    # isin: Language in ['eng', 'fre']
    print("\nisin demo (language in ['eng', 'fre']):")
    selected_langs = df[df['language'].isin(['eng', 'fre'])]
    print(selected_langs['language'].value_counts())
    logging.info("Demonstrated .isin selector")
    
    # between: rating between 3 and 4
    print("\nbetween demo (rating between 3 and 4):")
    mid_rated = df[df['rating'].between(3, 4)]
    print(mid_rated[['title', 'rating']].head())
    logging.info("Demonstrated .between selector")

    logging.info("=== Pandas Selector Demonstrations Completed ===")

if __name__ == "__main__":
    demonstrate_selectors()
