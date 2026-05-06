import pandas as pd
import logging

logger = logging.getLogger(__name__)

def report_missing(df: pd.DataFrame) -> pd.DataFrame:
    missing_count = df.isna().sum()
    missing_pct = (df.isna().mean() * 100).round(2)
    report = pd.DataFrame({
        'missing_count': missing_count,
        'missing_pct': missing_pct,
        'dtype': df.dtypes
    })
    report = report[report['missing_count'] > 0].sort_values(
        'missing_pct', ascending=False
    )
    logger.info('Missing value report generated for %d columns', len(report))
    return report

def handle_missing_values(df):
    """Applies different strategies to resolve missing data."""
    logger.info("Starting missing value handling...")
    
    # 1. Analysis
    missing_report = df.isnull().sum()
    logger.info(f"Missing values before handling:\n{missing_report[missing_report > 0]}")

    # 2. Strategies
    # Fill categorical/string with "Unknown"
    string_cols = ['author_name', 'publisher', 'genres', 'language', 'overview']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
            logger.info(f"Filled missing values in '{col}' with 'Unknown'")

    # Fill numeric 'rating' with median
    if 'rating' in df.columns:
        median_rating = df['rating'].median()
        df['rating'] = df['rating'].fillna(median_rating)
        logger.info(f"Filled missing values in 'rating' with median: {median_rating}")

    # Fill 'number_of_pages_median' with 0 or median
    if 'number_of_pages_median' in df.columns:
        df['number_of_pages_median'] = df['number_of_pages_median'].fillna(0)
        logger.info("Filled missing values in 'number_of_pages_median' with 0")

    # Drop rows if 'title' is missing (critical column)
    if 'title' in df.columns:
        before_count = len(df)
        df = df.dropna(subset=['title'])
        after_count = len(df)
        if before_count > after_count:
            logger.warning(f"Dropped {before_count - after_count} rows due to missing 'title'")

    return df
