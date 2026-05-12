import logging

def validate_data(df):
    """Performs logical checks and assertions on the cleaned dataset."""
    logging.info("Starting data validation...")
    
    # 1. No missing titles
    assert df['title'].isnull().sum() == 0, "Validation Failed: Found missing titles"
    
    # 2. Ratings within range [0, 5]
    if 'rating' in df.columns:
        invalid_ratings = df[(df['rating'] < 0) | (df['rating'] > 5)]
        assert invalid_ratings.empty, f"Validation Failed: Found {len(invalid_ratings)} ratings outside [0, 5] range"
        
    # 3. Year range check (e.g., not in the future)
    if 'first_publish_year' in df.columns:
        current_year = 2026 # Context date
        future_years = df[df['first_publish_year'] > current_year]
        assert future_years.empty, "Validation Failed: Found books from the future"

    logging.info("Data validation passed successfully")
    return True
