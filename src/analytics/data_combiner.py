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

def merge_mysql_mongodb(mysql_df, mongo_df, on='key', how='inner'):
    """
    Normalizes the join key to string and merges MySQL and MongoDB DataFrames.
    """
    logging.info(f"Merging MySQL and MongoDB data on '{on}' using '{how}' join.")
    
    # Normalize the join key to string
    mysql_df = mysql_df.copy()
    mongo_df = mongo_df.copy()
    mysql_df[on] = mysql_df[on].astype(str)
    mongo_df[on] = mongo_df[on].astype(str)
    
    merged_df = pd.merge(
        mysql_df, 
        mongo_df, 
        on=on, 
        how=how, 
        suffixes=('_mysql', '_mongo')
    )
    
    logging.info(f"Merge completed. Result shape: {merged_df.shape}")
    return merged_df

def demonstrate_join_types(mysql_df, mongo_df, on='key'):
    """
    Demonstrates all four join types and prints/logs row counts.
    
    Join Type Explanations:
    - Inner: Returns only rows with keys present in both datasets. Appropriate for strict matching.
    - Left: Keeps all rows from MySQL, filling missing data from MongoDB. Useful when MySQL is primary.
    - Right: Keeps all rows from MongoDB, filling missing data from MySQL. Useful when MongoDB is primary.
    - Outer: Keeps all rows from both. Best for identifying data gaps across all sources.
    """
    join_types = ['inner', 'outer', 'left', 'right']
    
    # Normalization for consistent comparison in demo
    m_df = mysql_df.copy()
    g_df = mongo_df.copy()
    m_df[on] = m_df[on].astype(str)
    g_df[on] = g_df[on].astype(str)
    
    print("\n--- JOIN TYPE DEMONSTRATION ---")
    for jt in join_types:
        result = pd.merge(m_df, g_df, on=on, how=jt)
        count = len(result)
        msg = f"Join Type: {jt:<5} | Row Count: {count}"
        print(msg)
        logging.info(f"Demonstration - {msg}")
    print("-------------------------------\n")

def concat_dataframes(dfs, reset_index=True):
    """
    Stacks a list of DataFrames with the same schema.
    """
    if not dfs:
        logging.warning("Attempted to concatenate an empty list of DataFrames.")
        return pd.DataFrame()
        
    logging.info(f"Concatenating {len(dfs)} DataFrames (reset_index={reset_index}).")
    result_df = pd.concat(dfs, ignore_index=reset_index)
    logging.info(f"Concatenation completed. Result shape: {result_df.shape}")
    return result_df

if __name__ == "__main__":
    # Quick internal sanity check if run directly
    data_mysql = {'key': ['/works/OL1', '/works/OL2'], 'val_m': [1, 2]}
    data_mongo = {'key': ['/works/OL2', '/works/OL3'], 'val_g': [2, 3]}
    
    df1 = pd.DataFrame(data_mysql)
    df2 = pd.DataFrame(data_mongo)
    
    print("Running demonstration:")
    demonstrate_join_types(df1, df2)
    
    print("\nMerging (inner):")
    merged = merge_mysql_mongodb(df1, df2)
    print(merged)
    
    print("\nConcatenating:")
    concatenated = concat_dataframes([df1, df2])
    print(concatenated)
