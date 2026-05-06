import pandas as pd
import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analytics.data_loader import get_mongo_data

# Ensure logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def generate_quality_report():
    logging.info("=== Starting Data Quality Report Generation ===")
    
    # Load data
    df = get_mongo_data()
    
    report_data = []
    
    for col in df.columns:
        # Handle unhashable types for uniqueness
        if df[col].apply(lambda x: isinstance(x, list)).any():
            unique_count = df[col].astype(str).nunique()
        else:
            unique_count = df[col].nunique()
            
        completeness = (df[col].count() / len(df)) * 100
        uniqueness = (unique_count / len(df)) * 100
        missing = df[col].isnull().sum()
        dtype = df[col].dtype
        
        report_data.append({
            "column": col,
            "dtype": dtype,
            "missing_values": missing,
            "completeness_pct": round(completeness, 2),
            "uniqueness_pct": round(uniqueness, 2)
        })
        
    quality_df = pd.DataFrame(report_data)
    
    # Save as CSV
    os.makedirs("data/processed/reports", exist_ok=True)
    report_path = "data/processed/reports/quality_report.csv"
    quality_df.to_csv(report_path, index=False)
    
    print("\n--- Data Quality Report ---")
    print(quality_df)
    print(f"\nReport saved to {report_path}")
    
    logging.info(f"Generated quality report with {len(df.columns)} columns")
    logging.info(f"Quality report saved to {report_path}")
    logging.info("=== Data Quality Report Generation Completed ===")

if __name__ == "__main__":
    generate_quality_report()
