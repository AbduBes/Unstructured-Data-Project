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

def wide_to_long(df, id_cols, value_cols, var_name='metric', value_name='value'):
    """
    Reshapes selected metric columns into long format using pd.melt().
    """
    logging.info(f"Reshaping DataFrame to long format. id_cols={id_cols}, value_cols={value_cols}")
    return pd.melt(df, id_vars=id_cols, value_vars=value_cols, var_name=var_name, value_name=value_name)

def long_to_wide(df, index, columns, values, aggfunc='mean'):
    """
    Restores wide format from long format using df.pivot_table().
    """
    logging.info(f"Reshaping DataFrame to wide format. index={index}, columns={columns}, values={values}")
    return df.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc)

def build_pivot_table(df, index, columns, values, aggfunc='mean'):
    """
    Builds an aggregated pivot table with margins=True and fills NaN with 0.
    """
    logging.info(f"Building pivot table. index={index}, columns={columns}, values={values}, aggfunc={aggfunc}")
    pivot = df.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc, margins=True)
    return pivot.fillna(0)

def build_crosstab(df, index_col, column_col, normalize=False):
    """
    Uses pd.crosstab() to count co-occurrences between two categorical columns.
    """
    logging.info(f"Building crosstab between {index_col} and {column_col}. normalize={normalize}")
    return pd.crosstab(df[index_col], df[column_col], normalize=normalize)
