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

def _get_primary_genre(genres):
    """
    Helper to extract the first genre from a list or comma-separated string.
    """
    if isinstance(genres, list) and len(genres) > 0:
        return genres[0]
    if isinstance(genres, str):
        parts = genres.split(',')
        return parts[0].strip() if parts else "Unknown"
    return "Unknown"

import matplotlib.pyplot as plt

def _save_chart(df, kind, title, filename, x=None, y=None):
    """
    Modular helper to save charts.
    """
    plt.figure(figsize=(10, 6))
    if kind == 'bar':
        if x and y:
            df.plot(kind='bar', x=x, y=y, legend=False)
        else:
            df.plot(kind='bar', legend=False)
    elif kind == 'line':
        df.plot(kind='line')
    
    plt.title(title)
    plt.tight_layout()
    output_dir = 'data/processed/outputs'
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path)
    plt.close()
    logging.info(f"Chart saved to {save_path}")

def top_genres_by_rating(df, n=10):
    """
    Returns top N genres by average rating, filtering for groups with >= 5 books.
    Saves a bar chart of the result.
    """
    logging.info(f"Calculating top {n} genres by rating.")
    temp_df = df.copy()
    temp_df['primary_genre'] = temp_df['genres'].apply(_get_primary_genre)
    
    stats = temp_df.groupby('primary_genre').agg(
        avg_rating=('rating', 'mean'),
        total_ratings=('ratings_count', 'sum'),
        book_count=('key', 'count')
    )
    
    filtered = stats[stats['book_count'] >= 5]
    result = filtered.sort_values(by='avg_rating', ascending=False).head(n)
    
    _save_chart(result['avg_rating'], 'bar', f'Top {n} Genres by Rating', 'top_genres.png')
    
    return result

def engagement_ratio_by_genre(df):
    """
    Calculates engagement ratio (ratings_count/edition_count) per book, 
    then aggregates by primary_genre. Saves a bar chart.
    """
    logging.info("Calculating engagement ratio by genre.")
    temp_df = df.copy()
    temp_df['primary_genre'] = temp_df['genres'].apply(_get_primary_genre)
    
    # Avoid division by zero
    temp_df['engagement_ratio'] = temp_df['ratings_count'] / temp_df['edition_count'].replace(0, 1)
    
    stats = temp_df.groupby('primary_genre').agg(
        avg_engagement=('engagement_ratio', 'mean'),
        avg_rating=('rating', 'mean'),
        book_count=('key', 'count')
    )
    
    result = stats.sort_values(by='avg_engagement', ascending=False).head(10)
    _save_chart(result['avg_engagement'], 'bar', 'Top 10 Genres by Engagement Ratio', 'engagement_ratio.png')
    
    return stats

def yearly_publishing_trends(df, start=1900, end=2024):
    """
    Analyzes publishing trends within a specific year range. Saves a line chart.
    """
    logging.info(f"Analyzing publishing trends from {start} to {end}.")
    filtered = df[(df['first_publish_year'] >= start) & (df['first_publish_year'] <= end)]
    
    trends = filtered.groupby('first_publish_year').agg(
        book_count=('key', 'count'),
        avg_rating=('rating', 'mean'),
        avg_pages=('number_of_pages_median', 'mean')
    )
    
    _save_chart(trends['book_count'], 'line', 'Yearly Publishing Trends', 'publishing_trends.png')
    
    return trends.sort_index()

def language_distribution(df, top_n=10):
    """
    Calculates the distribution and percentage share of books per language.
    Saves a bar chart.
    """
    logging.info(f"Calculating language distribution for top {top_n} languages.")
    dist = df['language'].value_counts().reset_index()
    dist.columns = ['language', 'book_count']
    
    total_books = dist['book_count'].sum()
    dist['percentage'] = (dist['book_count'] / total_books) * 100
    
    result = dist.head(top_n)
    _save_chart(result, 'bar', f'Top {top_n} Languages', 'lang_dist.png', x='language', y='book_count')
    
    return result
