"""
Automated chart generation module – Lab 12.
Loads the cleaned book dataset and generates all static and interactive charts.
"""

import logging
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Updated data path for book dataset
DATA_PATH = Path("data/processed/cleaned/cleaned_books.csv")
STATIC_OUT = Path("outputs/visualizations/static")
INTERACTIVE_OUT = Path("outputs/visualizations/interactive")


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load and lightly prepare the cleaned book dataset."""
    if not path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at '{path}'. "
            "Run the cleaning pipeline first."
        )
    df = pd.read_csv(path, low_memory=False)
    # Required fields based on BOOK_DATASET_MAPPING.md
    required = ["title", "first_publish_year", "genres",
                "edition_count", "number_of_pages_median", "rating",
                "ratings_count"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")
    logger.info("Loaded %d books from %s", len(df), path)
    return df


def run_static_charts(df: pd.DataFrame) -> dict:
    """Generate and save all matplotlib / seaborn charts."""
    from .static_charts import (
        plot_avg_rating_over_years,
        plot_subject_rating_boxplot,
        plot_correlation_heatmap,
        plot_subject_count_bar,
        plot_rating_vs_edition_count,
        plot_top_publishers_bar,
        plot_ratings_count_hist,
        plot_pages_distribution,
    )

    STATIC_OUT.mkdir(parents=True, exist_ok=True)
    results = {}

    charts = [
        ("avg_rating_over_years",    plot_avg_rating_over_years),
        ("subject_rating_boxplot",   plot_subject_rating_boxplot),
        ("correlation_heatmap",      plot_correlation_heatmap),
        ("subject_count_bar",        plot_subject_count_bar),
        ("rating_vs_edition_count",  plot_rating_vs_edition_count),
        ("top_publishers_bar",       plot_top_publishers_bar),
        ("ratings_count_dist",       plot_ratings_count_hist),
        ("pages_distribution",       plot_pages_distribution),
    ]

    for name, fn in charts:
        try:
            fig = fn(df, out_dir=STATIC_OUT, save=True)
            results[name] = fig
            print(f"  [static]  {name} - saved to {STATIC_OUT}")
        except Exception as exc:
            logger.error("Failed to generate '%s': %s", name, exc)
            print(f"  [static]  {name}  FAILED: {exc}")

    return results


def run_interactive_charts(df: pd.DataFrame) -> dict:
    """Generate and save all Plotly interactive charts."""
    from .interactive_charts import (
        interactive_editions_vs_pages,
        interactive_top_books_bar,
        interactive_books_per_year,
        interactive_subject_boxplot,
        interactive_book_dashboard,
    )

    INTERACTIVE_OUT.mkdir(parents=True, exist_ok=True)
    results = {}

    charts = [
        ("editions_vs_pages",     interactive_editions_vs_pages),
        ("top_books_bar",         interactive_top_books_bar),
        ("books_per_year",        interactive_books_per_year),
        ("subject_boxplot",       interactive_subject_boxplot),
        ("book_dashboard",        interactive_book_dashboard),
    ]

    for name, fn in charts:
        try:
            fig = fn(df, out_dir=INTERACTIVE_OUT, save=True)
            results[name] = fig
            print(f"  [interactive]  {name} - saved to {INTERACTIVE_OUT}")
        except Exception as exc:
            logger.error("Failed to generate '%s': %s", name, exc)
            print(f"  [interactive]  {name}  FAILED: {exc}")

    return results


def generate_all(data_path: Path = DATA_PATH) -> dict:
    """Full pipeline: load data → static charts → interactive charts."""
    print("\n========================================")
    print("  Lab 12 – Book Visualization Generator")
    print("========================================\n")

    df = load_data(data_path)
    print(f"Dataset: {len(df)} books, {len(df.columns)} columns\n")

    print("── Static charts (matplotlib / seaborn) ──")
    static = run_static_charts(df)

    print("\n── Interactive charts (Plotly Express) ──")
    interactive = run_interactive_charts(df)

    print("\n========================================")
    print(f"  Done!  {len(static)} static + {len(interactive)} interactive")
    print(f"  Static  → {STATIC_OUT}")
    print(f"  Interactive → {INTERACTIVE_OUT}")
    print("========================================\n")

    return {"static": static, "interactive": interactive}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_all()
