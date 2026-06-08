"""Interactive callbacks for the Book Analytics dashboard (Lab 13).

Callbacks are what make a Dash app interactive: whenever the user changes a
filter, types in the search box, or the live timer ticks, Dash runs the
matching function and replaces the figure on screen.

Design note
-----------
The figure-building logic is factored into plain functions
(``build_*_figure``) that take a DataFrame and return a Plotly figure. The
``@app.callback`` wrappers in :func:`register_callbacks` only handle wiring
(reading the filter values, calling :func:`dashboard.data_access.filter_books`,
then the builder). This keeps the callbacks tiny and lets the notebook test
each chart directly without spinning up a server.

Callback inventory (6 total, all with >=1 Input and 1 Output):

    Pattern  Callback            Trigger                      Output
    N -> 1   Top-books bar       genre + year + search        top-books-bar figure
    N -> 1   Rating box-plot     genre + year + search        rating-box figure
    N -> 1   Reach scatter       genre + year + search        scatter-plot figure
    N -> 1   Year trend line     genre + year + search        trend-line figure
    N -> N   KPI cards           genre + year + search        four card values
    1 -> 1   Live ticker         dcc.Interval tick            live-ticker figure
"""

from __future__ import annotations

import random
from collections import deque
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output

from dashboard import data_access

# Shared visual style so every chart matches the dark Bootstrap theme.
CHART_TEMPLATE = "plotly_dark"
TRANSPARENT = "rgba(0,0,0,0)"
ACCENT = "#0d6efd"

# Rolling buffer for the simulated live stream (kept small to bound memory).
_LIVE_BUFFER: "deque[tuple[str, float]]" = deque(maxlen=30)


# --------------------------------------------------------------------------- #
# Styling helpers
# --------------------------------------------------------------------------- #
def _style(fig: go.Figure) -> go.Figure:
    """Apply the shared dark, transparent-background styling to a figure."""
    fig.update_layout(
        template=CHART_TEMPLATE,
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        margin=dict(l=40, r=20, t=30, b=40),
        font=dict(family="Inter, system-ui, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
    )
    return fig


def empty_figure(message: str = "No data for the current filters") -> go.Figure:
    """Return a clean placeholder figure instead of letting a chart break."""
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(size=15, color="#aaa"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _style(fig)


# --------------------------------------------------------------------------- #
# Pure figure builders (also imported by the notebook for testing)
# --------------------------------------------------------------------------- #
def build_top_books_figure(df: pd.DataFrame, n: int = 12) -> go.Figure:
    """Horizontal bar of the top-``n`` books by reach (ratings count)."""
    if df.empty or "ratings_count" not in df.columns:
        return empty_figure()
    top = (
        df.dropna(subset=["ratings_count"])
        .nlargest(n, "ratings_count")
        .sort_values("ratings_count")
    )
    if top.empty:
        return empty_figure()
    fig = px.bar(
        top,
        x="ratings_count",
        y="title",
        orientation="h",
        color="ratings_count",
        color_continuous_scale="Blues",
        labels={"ratings_count": "Ratings Count", "title": ""},
        hover_data={"genres": True, "first_publish_year": True, "rating": ":.2f"},
    )
    fig.update_layout(coloraxis_showscale=False)
    return _style(fig)


def build_rating_figure(df: pd.DataFrame, max_genres: int = 10) -> go.Figure:
    """Box plot of rating distribution for the most common genres."""
    if df.empty or "rating" not in df.columns or "genres" not in df.columns:
        return empty_figure()
    top_genres = df["genres"].value_counts().head(max_genres).index.tolist()
    data = df[df["genres"].isin(top_genres)]
    if data.empty:
        return empty_figure()
    order = (
        data.groupby("genres")["rating"].median().sort_values(ascending=False).index.tolist()
    )
    fig = px.box(
        data,
        x="genres",
        y="rating",
        color="genres",
        category_orders={"genres": order},
        labels={"genres": "", "rating": "Rating (0-5)"},
        hover_data={"title": True},
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(tickangle=-30)
    return _style(fig)


def build_scatter_figure(df: pd.DataFrame) -> go.Figure:
    """Scatter of editions (distribution breadth) vs reach (ratings count)."""
    needed = {"edition_count", "ratings_count", "rating"}
    if df.empty or not needed.issubset(df.columns):
        return empty_figure()
    data = df[(df["edition_count"] > 0) & (df["ratings_count"].notna())]
    if data.empty:
        return empty_figure()
    fig = px.scatter(
        data,
        x="edition_count",
        y="ratings_count",
        color="rating",
        color_continuous_scale="Viridis",
        size="ratings_count",
        hover_name="title",
        labels={
            "edition_count": "Number of Editions",
            "ratings_count": "Ratings Count (reach)",
            "rating": "Rating",
        },
    )
    return _style(fig)


def build_trend_figure(df: pd.DataFrame) -> go.Figure:
    """Line chart: number of books published per year (within current filters)."""
    if df.empty or "first_publish_year" not in df.columns:
        return empty_figure()
    yearly = (
        df.groupby("first_publish_year")
        .agg(book_count=("title", "count"), avg_rating=("rating", "mean"))
        .reset_index()
        .sort_values("first_publish_year")
    )
    if yearly.empty:
        return empty_figure()
    fig = px.line(
        yearly,
        x="first_publish_year",
        y="book_count",
        markers=True,
        labels={"first_publish_year": "Year", "book_count": "Books Published"},
        hover_data={"avg_rating": ":.2f"},
    )
    fig.update_traces(line_color=ACCENT, line_width=2.5, marker=dict(size=6))
    return _style(fig)


def build_live_figure() -> go.Figure:
    """Render the current contents of the simulated live-stream buffer."""
    if not _LIVE_BUFFER:
        return empty_figure("Waiting for live data...")
    times = [t for t, _ in _LIVE_BUFFER]
    values = [v for _, v in _LIVE_BUFFER]
    fig = go.Figure(
        go.Scatter(
            x=times,
            y=values,
            mode="lines+markers",
            line=dict(color="#dc3545", width=2),
            fill="tozeroy",
            fillcolor="rgba(220,53,69,0.15)",
            name="Live views/sec",
        )
    )
    fig.update_layout(yaxis_title="Simulated views/sec", xaxis_title="Time")
    return _style(fig)


# --------------------------------------------------------------------------- #
# Registration: wire the builders to the Dash components.
# --------------------------------------------------------------------------- #
def register_callbacks(app) -> None:
    """Attach every dashboard callback to ``app``. Called once from app.py."""

    filter_inputs = (
        Input("genre-filter", "value"),
        Input("year-slider", "value"),
        Input("search-input", "value"),
    )

    # --- N -> 1: top books bar -------------------------------------------- #
    @app.callback(Output("top-books-bar", "figure"), *filter_inputs)
    def _update_top_books(genre, year_range, search):
        data = data_access.filter_books(genre=genre, year_range=year_range, search=search)
        return build_top_books_figure(data)

    # --- N -> 1: rating box plot ------------------------------------------ #
    @app.callback(Output("rating-box", "figure"), *filter_inputs)
    def _update_rating(genre, year_range, search):
        data = data_access.filter_books(genre=genre, year_range=year_range, search=search)
        return build_rating_figure(data)

    # --- N -> 1: editions vs reach scatter -------------------------------- #
    @app.callback(Output("scatter-plot", "figure"), *filter_inputs)
    def _update_scatter(genre, year_range, search):
        data = data_access.filter_books(genre=genre, year_range=year_range, search=search)
        return build_scatter_figure(data)

    # --- N -> 1: books-per-year trend ------------------------------------- #
    @app.callback(Output("trend-line", "figure"), *filter_inputs)
    def _update_trend(genre, year_range, search):
        data = data_access.filter_books(genre=genre, year_range=year_range, search=search)
        return build_trend_figure(data)

    # --- N -> N: KPI cards ------------------------------------------------- #
    @app.callback(
        Output("kpi-total", "children"),
        Output("kpi-avg-rating", "children"),
        Output("kpi-total-ratings", "children"),
        Output("kpi-avg-pages", "children"),
        *filter_inputs,
    )
    def _update_kpis(genre, year_range, search):
        data = data_access.filter_books(genre=genre, year_range=year_range, search=search)
        if data.empty:
            return "0", "-", "0", "-"
        total = f"{len(data):,}"
        avg_rating = f"{data['rating'].mean():.2f}" if "rating" in data else "-"
        total_ratings = (
            f"{int(data['ratings_count'].fillna(0).sum()):,}"
            if "ratings_count" in data else "-"
        )
        avg_pages = (
            f"{data['number_of_pages_median'].mean():.0f}"
            if "number_of_pages_median" in data else "-"
        )
        return total, avg_rating, total_ratings, avg_pages

    # --- 1 -> 1: live ticker (driven by dcc.Interval) --------------------- #
    @app.callback(Output("live-ticker", "figure"), Input("live-interval", "n_intervals"))
    def _update_live(_n):
        # In a real system this would read from a streaming source / WebSocket
        # buffer. Here we simulate a new reading on every interval tick.
        now = datetime.now().strftime("%H:%M:%S")
        new_value = round(random.uniform(50, 500), 1)
        _LIVE_BUFFER.append((now, new_value))
        return build_live_figure()
