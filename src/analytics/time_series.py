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

def parse_and_extract_dates(df, date_col='first_publish_year'):
    """
    Parses a column to datetime64 and extracts year, month, and decade.
    """
    logging.info(f"Parsing '{date_col}' to datetime and extracting components.")
    df = df.copy()
    # Treat integer year as Jan 1st
    df['publish_date'] = pd.to_datetime(df[date_col], format='%Y', errors='coerce')
    
    df['year'] = df['publish_date'].dt.year
    df['month'] = df['publish_date'].dt.month
    df['decade'] = (df['year'] // 10) * 10
    
    return df

def resample_yearly(df, date_index_col='publish_date'):
    """
    Resamples the DataFrame to yearly frequency and returns counts.
    """
    logging.info(f"Resampling data to yearly frequency using '{date_index_col}'.")
    ts_df = df.dropna(subset=[date_index_col])
    return ts_df.set_index(date_index_col).resample('YE').size()

def compute_rolling_averages(df, value_col, windows=[3, 5], date_col='publish_date'):
    """
    Computes rolling averages for a given column with multiple window sizes.
    """
    logging.info(f"Computing rolling averages for '{value_col}' with windows {windows}.")
    df = df.dropna(subset=[date_col]).sort_values(date_col).copy()
    
    for w in windows:
        df[f'rolling_avg_{w}'] = df[value_col].rolling(window=w).mean()
        
    return df
