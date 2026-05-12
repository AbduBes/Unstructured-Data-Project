import pandas as pd
import logging
import os
import sys

# Ensure src is in sys.path for internal imports if needed
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Configure logging
logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def genre_summary(df):
    """
    Groups by genres and returns avg_rating, total_ratings, avg_pages, book_count.
    """
    logging.info("Calculating genre summary.")
    summary = df.groupby('genres').agg(
        avg_rating=('rating', 'mean'),
        total_ratings=('ratings_count', 'sum'),
        avg_pages=('number_of_pages_median', 'mean'),
        book_count=('key', 'count')
    )
    return summary

def yearly_trends(df, start=1900, end=2024):
    """
    Filters by first_publish_year, groups by year, returns trend metrics.
    """
    logging.info(f"Calculating yearly trends from {start} to {end}.")
    filtered_df = df[(df['first_publish_year'] >= start) & (df['first_publish_year'] <= end)]
    trends = filtered_df.groupby('first_publish_year').agg(
        book_count=('key', 'count'),
        avg_rating=('rating', 'mean'),
        total_ratings=('ratings_count', 'sum'),
        avg_pages=('number_of_pages_median', 'mean')
    )
    return trends

def top_n_per_group(df, group_col, value_col, n=3):
    """
    Returns the top N books per group sorted by value_col descending.
    """
    logging.info(f"Calculating top {n} books per group '{group_col}' based on '{value_col}'.")
    top_n = df.sort_values(value_col, ascending=False).groupby(group_col).head(n)
    return top_n

def rating_distribution(df):
    """
    Calculates descriptive statistics of ratings grouped by genres.
    """
    logging.info("Calculating rating distribution per genre.")
    dist = df.groupby('genres')['rating'].agg(["mean", "std", "min", "max"])
    return dist
