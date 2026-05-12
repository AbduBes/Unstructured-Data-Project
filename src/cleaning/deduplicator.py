import pandas as pd
import logging

def remove_duplicates(df):
    """Removes exact duplicate rows and repeated IDs."""
    logging.info("Starting deduplication...")
    
    initial_count = len(df)
    
    # Handle unhashable types (lists) for drop_duplicates
    # We create a version of df where lists are strings for the check
    df_temp = df.copy()
    for col in df_temp.columns:
        if df_temp[col].apply(lambda x: isinstance(x, list)).any():
            df_temp[col] = df_temp[col].astype(str)
    
    # Identify duplicates using the hashable version
    duplicate_mask = df_temp.duplicated()
    df = df[~duplicate_mask]
    
    after_exact = len(df)
    logging.info(f"Removed {initial_count - after_exact} exact duplicate rows")
    
    # Remove repeated IDs (key)
    if 'key' in df.columns:
        df = df.drop_duplicates(subset=['key'])
        final_count = len(df)
        logging.info(f"Removed {after_exact - final_count} duplicate 'key' records")
        
    logging.info(f"Row count: Before={initial_count}, After={len(df)}")
    return df
