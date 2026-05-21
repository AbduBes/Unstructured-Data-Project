"""
Static visualization module for Movie Industry Analytics Pipeline.
Uses matplotlib (object-oriented API) and seaborn for all static charts.
Lab 12 - Data Visualization
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

sns.set_theme(style="whitegrid")
sns.set_context("notebook")
sns.set_palette("viridis")

STATIC_OUT = Path("outputs/visualizations/static")

def _save(fig: plt.Figure, stem: str, out_dir: Path = STATIC_OUT) -> dict:
    """Save figure as PNG (300 dpi) and PDF. Returns dict of saved paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / f"{stem}.png"
    pdf_path = out_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    logger.info("Saved %s  (PNG + PDF)", stem)
    return {"png": str(png_path), "pdf": str(pdf_path)}

def plot_avg_rating_over_years(df: pd.DataFrame,
                               out_dir: Path = STATIC_OUT,
                               save: bool = True) -> plt.Figure:
    """Line chart: mean rating and book count per first publish year."""
    yearly = (df.groupby("first_publish_year")
               .agg(avg_rating=("rating", "mean"),
                    book_count=("title", "count"))
               .reset_index()
               .query("first_publish_year >= 1900 and first_publish_year <= 2025"))

    fig, ax1 = plt.subplots(figsize=(12, 5))
    color_line = "#1a6faf"
    color_bar = "#a8d5e2"

    ax1.bar(yearly["first_publish_year"], yearly["book_count"],
            color=color_bar, alpha=0.5, label="Book Count")
    ax1.set_ylabel("Number of Books", color=color_bar, fontsize=11)
    ax1.tick_params(axis="y", labelcolor=color_bar)

    ax2 = ax1.twinx()
    ax2.plot(yearly["first_publish_year"], yearly["avg_rating"],
             color=color_line, linewidth=2.5, marker="o", markersize=5,
             label="Avg. Rating")
    ax2.set_ylabel("Average Rating (0–5)", color=color_line, fontsize=11)
    ax2.tick_params(axis="y", labelcolor=color_line)
    ax2.set_ylim(0, 5)

    ax1.set_xlabel("First Publish Year", fontsize=11)
    ax1.set_title("Book Publications and Average Rating Over the Years",
                  fontsize=14, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    fig.tight_layout()
    if save:
        _save(fig, "avg_rating_over_years", out_dir)
    return fig


# ── 5. Box plot – Rating by subject (seaborn) ────────────────────────────────
def plot_subject_rating_boxplot(df: pd.DataFrame,
                                out_dir: Path = STATIC_OUT,
                                save: bool = True) -> plt.Figure:
    """Box-and-whisker plot: rating per subject/genre."""
    # Group by 'genres' (which was mapped from 'subject')
    order = (df.groupby("genres")["rating"]
               .median().sort_values(ascending=False).index.tolist())

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df, x="genres", y="rating",
                order=order, hue="genres", palette="viridis",
                legend=False, ax=ax)
    ax.set_xlabel("Subject/Genre", fontsize=11)
    ax.set_ylabel("Average Rating (0–5)", fontsize=11)
    ax.set_title("Book Rating Distribution by Subject", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()

    if save:
        _save(fig, "subject_rating_boxplot", out_dir)
    return fig

# ── 6. Heatmap – Correlation matrix ──────────────────────────────────────────
def plot_correlation_heatmap(df: pd.DataFrame,
                             out_dir: Path = STATIC_OUT,
                             save: bool = True) -> plt.Figure:
    """seaborn heatmap of numeric book feature correlations."""
    numeric_cols = ["rating", "ratings_count", "first_publish_year", 
                    "edition_count", "number_of_pages_median"]
    corr_cols = [c for c in numeric_cols if c in df.columns]
    corr = df[corr_cols].corr()

    labels = {
        "rating": "Rating",
        "ratings_count": "Rating Count",
        "first_publish_year": "Pub Year",
        "edition_count": "Editions",
        "number_of_pages_median": "Pages",
    }
    corr.index = [labels.get(c, c) for c in corr.index]
    corr.columns = [labels.get(c, c) for c in corr.columns]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, vmin=-1, vmax=1, square=True,
                linewidths=0.5, ax=ax,
                annot_kws={"size": 10})
    ax.set_title("Correlation Matrix – Ratings, Editions, Pages, Year",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()

    if save:
        _save(fig, "correlation_heatmap", out_dir)
    return fig


# ── 7. Bar chart – Subject distribution ──────────────────────────────────────
def plot_subject_count_bar(df: pd.DataFrame,
                           out_dir: Path = STATIC_OUT,
                           save: bool = True) -> plt.Figure:
    """Vertical bar chart: number of books per subject."""
    counts = df["genres"].value_counts()

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(counts.index, counts.values,
                  color=sns.color_palette("viridis", len(counts)))
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(int(bar.get_height())), ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Subject/Genre", fontsize=11)
    ax.set_ylabel("Number of Books", fontsize=11)
    ax.set_title("Number of Books per Subject", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()

    if save:
        _save(fig, "subject_count_bar", out_dir)
    return fig

# ── 8. Scatter plot – Rating vs Edition Count ────────────────────────────────
def plot_rating_vs_edition_count(df: pd.DataFrame,
                                 out_dir: Path = STATIC_OUT,
                                 save: bool = True) -> plt.Figure:
    """Scatter plot showing relationship between edition count and rating."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x="edition_count", y="rating", 
                    alpha=0.6, hue="genres", palette="viridis", ax=ax)
    
    ax.set_xlabel("Number of Editions", fontsize=11)
    ax.set_ylabel("Average Rating (0–5)", fontsize=11)
    ax.set_title("Relationship: Edition Count vs. Average Rating", 
                 fontsize=14, fontweight="bold")
    ax.legend(title="Subject", bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()

    if save:
        _save(fig, "rating_vs_edition_count", out_dir)
    return fig

# ── 9. Bar chart – Top Publishers ────────────────────────────────────────────
def plot_top_publishers_bar(df: pd.DataFrame, n: int = 10,
                            out_dir: Path = STATIC_OUT,
                            save: bool = True) -> plt.Figure:
    """Vertical bar chart: top-n publishers by book count."""
    counts = df["publisher"].value_counts().nlargest(n)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(counts.index, counts.values,
                  color=sns.color_palette("magma", len(counts)))
    
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(int(bar.get_height())), ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Publisher", fontsize=11)
    ax.set_ylabel("Number of Books", fontsize=11)
    ax.set_title(f"Top {n} Publishers by Book Count", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    if save:
        _save(fig, "top_publishers_bar", out_dir)
    return fig

# ── 10. Histogram – Ratings Count Distribution ──────────────────────────────
def plot_ratings_count_hist(df: pd.DataFrame,
                            out_dir: Path = STATIC_OUT,
                            save: bool = True) -> plt.Figure:
    """Histogram of ratings_count to show engagement distribution."""
    fig, ax = plt.subplots(figsize=(10, 6))
    # Filter out 0 or NaN for a cleaner distribution
    data = df[df["ratings_count"] > 0]["ratings_count"]
    
    sns.histplot(data, bins=30, kde=True, color="#d9534f", ax=ax)
    
    ax.set_xlabel("Number of Reader Ratings", fontsize=11)
    ax.set_ylabel("Frequency", fontsize=11)
    ax.set_title("Distribution of Reader Engagement (Ratings Count)", 
                 fontsize=14, fontweight="bold")
    fig.tight_layout()

    if save:
        _save(fig, "ratings_count_dist", out_dir)
    return fig

# ── 11. Histogram – Page Count Distribution ───────────────────────────────────
def plot_pages_distribution(df: pd.DataFrame,
                            out_dir: Path = STATIC_OUT,
                            save: bool = True) -> plt.Figure:
    """Histogram/KDE of median page counts."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df["number_of_pages_median"].dropna(), kde=True, 
                 color="#1a6faf", ax=ax)
    
    ax.set_xlabel("Median Number of Pages", fontsize=11)
    ax.set_ylabel("Frequency", fontsize=11)
    ax.set_title("Distribution of Book Page Counts", 
                 fontsize=14, fontweight="bold")
    fig.tight_layout()

    if save:
        _save(fig, "pages_distribution", out_dir)
    return fig
