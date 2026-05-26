"""
Interactive visualization module for Movie Industry Analytics Pipeline.
Uses Plotly Express (and Graph Objects for the multi-layout chart).
Lab 12 - Data Visualization
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

INTERACTIVE_OUT = Path("outputs/visualizations/interactive")
TEMPLATE = "plotly_white"


def _save_html(fig: go.Figure, stem: str,
               out_dir: Path = INTERACTIVE_OUT) -> go.Figure:
    """Write an interactive HTML file. Returns the figure object."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{stem}.html"
    fig.write_html(str(path))
    logger.info("Saved interactive chart: %s", path)
    return fig


# ── 1. Scatter – Editions vs Pages (interactive) ─────────────────────────────
def interactive_editions_vs_pages(df: pd.DataFrame,
                                  out_dir: Path = INTERACTIVE_OUT,
                                  save: bool = True) -> go.Figure:
    """Interactive scatter: edition count vs median page count."""
    # Ensure no NaNs in size column (ratings_count)
    data = df[(df["edition_count"] > 0) & 
              (df["number_of_pages_median"] > 0) &
              (df["ratings_count"].notna())].copy()

    fig = px.scatter(
        data,
        x="edition_count",
        y="number_of_pages_median",
        color="genres",
        size="ratings_count",
        hover_name="title",
        hover_data={
            "first_publish_year": True,
            "rating": ":.2f",
            "edition_count": True,
            "number_of_pages_median": True,
        },
        labels={
            "edition_count": "Number of Editions", 
            "number_of_pages_median": "Median Page Count"
        },
        title="Editions vs Page Count – Interactive Book Explorer",
        template=TEMPLATE,
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )

    fig.update_layout(
        legend_title="Subject",
        font=dict(family="Inter", size=13),
        height=580,
    )
    if save:
        _save_html(fig, "editions_vs_pages_interactive", out_dir)
    return fig


# ── 2. Bar – Top 10 books by rating count ────────────────────────────────────
def interactive_top_books_bar(df: pd.DataFrame, n: int = 10,
                              out_dir: Path = INTERACTIVE_OUT,
                              save: bool = True) -> go.Figure:
    """Interactive grouped bar: top-n books by rating count."""
    top = df.nlargest(n, "ratings_count")[
        ["title", "ratings_count", "edition_count", "rating",
         "first_publish_year", "genres"]
    ].copy()

    fig = px.bar(
        top.sort_values("ratings_count", ascending=True),
        x="ratings_count",
        y="title",
        orientation="h",
        color="genres",
        hover_name="title",
        hover_data={
            "first_publish_year": True,
            "rating": ":.2f",
            "edition_count": True,
            "ratings_count": True,
        },
        labels={"ratings_count": "Number of Ratings", "title": "Book"},
        title=f"Top {n} Books by Number of Ratings",
        template=TEMPLATE,
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig.update_layout(
        legend_title="Subject",
        font=dict(family="Inter", size=13),
        height=500,
    )
    if save:
        _save_html(fig, "top_books_ratings_bar", out_dir)
    return fig


# ── 3. Line – Books published per year ────────────────────────────────────────
def interactive_books_per_year(df: pd.DataFrame,
                               out_dir: Path = INTERACTIVE_OUT,
                               save: bool = True) -> go.Figure:
    """Interactive line: number of books published per year (1900–2025)."""
    yearly = (df.query("first_publish_year >= 1900 and first_publish_year <= 2025")
               .groupby("first_publish_year")
               .agg(
                   book_count=("title", "count"),
                   avg_rating=("rating", "mean"),
                   total_editions=("edition_count", "sum"),
               )
               .reset_index())

    fig = px.line(
        yearly,
        x="first_publish_year",
        y="book_count",
        markers=True,
        hover_data={
            "avg_rating": ":.2f",
            "total_editions": True,
            "book_count": True,
        },
        labels={"first_publish_year": "Year", "book_count": "Number of Books"},
        title="Books Published per Year (1900–2025)",
        template=TEMPLATE,
    )
    fig.update_traces(line_color="#1a6faf", line_width=2.5,
                      marker=dict(size=7))
    fig.update_layout(font=dict(family="Inter", size=13), height=450)
    if save:
        _save_html(fig, "books_per_year_line", out_dir)
    return fig


# ── 4. Box – Rating by subject (interactive) ─────────────────────────────────
def interactive_subject_boxplot(df: pd.DataFrame,
                                 out_dir: Path = INTERACTIVE_OUT,
                                 save: bool = True) -> go.Figure:
    """Interactive box plot: rating distribution per subject/genre."""
    order = (df.groupby("genres")["rating"]
               .median().sort_values(ascending=False).index.tolist())

    fig = px.box(
        df,
        x="genres",
        y="rating",
        category_orders={"genres": order},
        color="genres",
        hover_name="title",
        hover_data={
            "first_publish_year": True, 
            "rating": ":.2f",
            "author_name": True, # Added 3rd field
            "edition_count": True # Added 4th field
        },
        labels={"genres": "Subject", "rating": "Average Rating (0–5)"},
        title="Book Rating Distribution by Subject",
        template=TEMPLATE,
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig.update_layout(
        showlegend=False,
        font=dict(family="Inter", size=13),
        height=500,
    )
    if save:
        _save_html(fig, "subject_rating_boxplot_interactive", out_dir)
    return fig


# ── 5. Multi-layout – 2×2 interactive book dashboard ─────────────────────────
def interactive_book_dashboard(df: pd.DataFrame,
                               out_dir: Path = INTERACTIVE_OUT,
                               save: bool = True) -> go.Figure:
    """2×2 Plotly subplot combining ratings, editions, subject, and timeline."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Top 10 Books by Rating Count",
            "Rating Distribution",
            "Books per Subject",
            "Editions vs Page Count",
        ),
        vertical_spacing=0.14,
        horizontal_spacing=0.10,
    )

    # Panel 1 – top 10 ratings count
    top10 = df.nlargest(10, "ratings_count").sort_values("ratings_count")
    fig.add_trace(
        go.Bar(x=top10["ratings_count"], y=top10["title"],
               orientation="h",
               marker_color="#1a6faf",
               name="Ratings Count",
               # Added author_name and rating for >3 fields
               hovertemplate="<b>%{y}</b><br>Author: %{customdata[0]}<br>Rating: %{customdata[1]:.2f}<br>Count: %{x} ratings<extra></extra>",
               customdata=top10[['author_name', 'rating']]),
        row=1, col=1,
    )

    # Panel 2 – rating histogram
    fig.add_trace(
        go.Histogram(x=df["rating"].dropna(), nbinsx=10,
                     marker_color="#2ca02c", name="Ratings",
                     # Histogram tooltips are trickier, but we can add info
                     hovertemplate="Rating Range: %{x}<br>Frequency: %{y}<br>Dataset: Open Library<extra></extra>"),
        row=1, col=2,
    )

    # Panel 3 – subject count bar
    counts = df["genres"].value_counts()
    fig.add_trace(
        go.Bar(x=counts.index, y=counts.values,
               marker_color="#ff7f0e", name="Subject count",
               hovertemplate="Subject: %{x}<br>Count: %{y} books<br>Ref: OpenLibrary Docs<extra></extra>"),
        row=2, col=1,
    )

    # Panel 4 – editions vs pages scatter
    scatter_data = df[(df["edition_count"] > 0) & (df["number_of_pages_median"] > 0)]
    fig.add_trace(
        go.Scatter(
            x=scatter_data["edition_count"],
            y=scatter_data["number_of_pages_median"],
            mode="markers",
            marker=dict(
                color=scatter_data["rating"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Rating", x=1.02, len=0.45, y=0.12),
                size=8, opacity=0.7,
            ),
            text=scatter_data["title"],
            name="Books",
            hovertemplate="%{text}<br>Editions: %{x}<br>Pages: %{y}<extra></extra>",
        ),
        row=2, col=2,
    )

    fig.update_layout(
        title_text="Book Dataset Analytics Dashboard",
        title_font=dict(size=18),
        template=TEMPLATE,
        height=700,
        width=1100,
        showlegend=False,
        font=dict(family="Inter", size=11),
    )
    # axis labels
    fig.update_xaxes(title_text="Number of Ratings", row=1, col=1)
    fig.update_xaxes(title_text="Average Rating", row=1, col=2)
    fig.update_xaxes(title_text="Subject", row=2, col=1)
    fig.update_xaxes(title_text="Number of Editions", row=2, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_yaxes(title_text="Median Pages", row=2, col=2)

    if save:
        _save_html(fig, "interactive_dashboard", out_dir)
    return fig