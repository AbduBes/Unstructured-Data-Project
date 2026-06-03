"""Dash page layout for the Book Analytics dashboard (Lab 13).

The layout is kept separate from ``app.py`` so the entry point stays tiny and
the page structure is easy to read and test. The dataset is loaded **once**
here to populate the genre dropdown and the year-range slider; the actual
chart data is fetched again (filtered) inside the callbacks.

Structure of the page, top to bottom:

1. Header / title bar.
2. A row of KPI cards (total books, average rating, total ratings, avg pages).
3. A filter bar: genre dropdown, year range slider, title search box.
4. Four charts that all react to the filters:
   top books bar, rating box-plot, editions-vs-reach scatter, books-per-year trend.
5. A simulated live-data ticker driven by ``dcc.Interval``.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard import data_access

# --------------------------------------------------------------------------- #
# Load the dataset once to drive the filter widgets.
# --------------------------------------------------------------------------- #
_DF = data_access.load_data()
_GENRES = data_access.get_genres(_DF)
_YEAR_MIN, _YEAR_MAX = data_access.get_year_bounds(_DF)

# A handful of evenly spaced marks for the slider (avoids a cluttered axis).
_SLIDER_MARKS = {
    int(y): str(int(y))
    for y in range(_YEAR_MIN, _YEAR_MAX + 1, max(1, (_YEAR_MAX - _YEAR_MIN) // 8))
}

CARD_STYLE = {"textAlign": "center"}


# --------------------------------------------------------------------------- #
# Small helper: build a KPI card. Keeps the layout DRY.
# --------------------------------------------------------------------------- #
def kpi_card(card_id: str, label: str, value: str, icon: str = "") -> dbc.Card:
    """Return a Bootstrap card showing a single summary metric.

    The value sits in an element with ``id=card_id`` so a callback can update
    it whenever the filters change.
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(f"{icon} {label}".strip(),
                         className="text-muted small text-uppercase"),
                html.H3(value, id=card_id, className="mt-2 mb-0 fw-bold"),
            ],
            style=CARD_STYLE,
        ),
        className="shadow-sm h-100",
    )


def _kpi_row() -> dbc.Row:
    """Initial KPI cards (values are refreshed by a callback)."""
    total = len(_DF)
    avg_rating = f"{_DF['rating'].mean():.2f}" if "rating" in _DF else "-"
    total_ratings = (
        f"{int(_DF['ratings_count'].fillna(0).sum()):,}"
        if "ratings_count" in _DF else "-"
    )
    avg_pages = (
        f"{_DF['number_of_pages_median'].mean():.0f}"
        if "number_of_pages_median" in _DF else "-"
    )
    return dbc.Row(
        [
            dbc.Col(kpi_card("kpi-total", "Books", f"{total:,}", "📚"), md=3, xs=6),
            dbc.Col(kpi_card("kpi-avg-rating", "Avg Rating", avg_rating, "⭐"), md=3, xs=6),
            dbc.Col(kpi_card("kpi-total-ratings", "Total Ratings", total_ratings, "👥"), md=3, xs=6),
            dbc.Col(kpi_card("kpi-avg-pages", "Avg Pages", avg_pages, "📄"), md=3, xs=6),
        ],
        className="g-3 mb-4",
    )


def _filter_bar() -> dbc.Card:
    """Genre dropdown + year range slider + title search box."""
    return dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Genre", html_for="genre-filter"),
                            dcc.Dropdown(
                                id="genre-filter",
                                options=[{"label": g, "value": g} for g in _GENRES],
                                value=None,
                                placeholder="All genres",
                                clearable=True,
                            ),
                        ],
                        md=4, xs=12,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Publication Year Range", html_for="year-slider"),
                            dcc.RangeSlider(
                                id="year-slider",
                                min=_YEAR_MIN,
                                max=_YEAR_MAX,
                                value=[_YEAR_MIN, _YEAR_MAX],
                                marks=_SLIDER_MARKS,
                                step=1,
                                tooltip={"placement": "bottom", "always_visible": False},
                                allowCross=False,
                            ),
                        ],
                        md=5, xs=12,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Search Title", html_for="search-input"),
                            dbc.Input(
                                id="search-input",
                                type="text",
                                placeholder="e.g. Dune",
                                debounce=True,
                            ),
                        ],
                        md=3, xs=12,
                    ),
                ],
                className="g-3 align-items-end",
            )
        ),
        className="shadow-sm mb-4",
    )


def _chart_card(title: str, graph_id: str) -> dbc.Card:
    """A titled card wrapping a single ``dcc.Graph``."""
    return dbc.Card(
        [
            dbc.CardHeader(title, className="fw-semibold"),
            dbc.CardBody(
                dcc.Graph(id=graph_id, config={"displayModeBar": False},
                          style={"height": "380px"})
            ),
        ],
        className="shadow-sm mb-4 h-100",
    )


def build_layout() -> dbc.Container:
    """Assemble and return the full dashboard layout."""
    header = dbc.Row(
        dbc.Col(
            [
                html.H2("📚 Book Analytics — Live Dashboard", className="mb-1"),
                html.P(
                    f"Interactive view of {len(_DF):,} books "
                    f"({_YEAR_MIN}–{_YEAR_MAX}). Source: "
                    f"{data_access.get_source().upper()}.",
                    className="text-muted",
                ),
            ],
            className="py-3",
        )
    )

    charts_top = dbc.Row(
        [
            dbc.Col(_chart_card("Top Books by Reach (Ratings Count)", "top-books-bar"), lg=6),
            dbc.Col(_chart_card("Rating Distribution by Genre", "rating-box"), lg=6),
        ],
        className="g-0",
    )

    charts_bottom = dbc.Row(
        [
            dbc.Col(_chart_card("Editions vs Reach", "scatter-plot"), lg=6),
            dbc.Col(_chart_card("Books Published per Year", "trend-line"), lg=6),
        ],
        className="g-0",
    )

    live_section = dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.Span("📡 Live Stream Ticker ", className="fw-semibold"),
                    dbc.Badge("LIVE", color="danger", className="ms-2"),
                    html.Small(" — simulated feed, updates every 2s",
                               className="text-muted ms-2"),
                ]
            ),
            dbc.CardBody(
                dcc.Graph(id="live-ticker", config={"displayModeBar": False},
                          style={"height": "300px"})
            ),
        ],
        className="shadow-sm mb-4",
    )

    return dbc.Container(
        [
            header,
            _kpi_row(),
            _filter_bar(),
            charts_top,
            charts_bottom,
            live_section,
            # Drives the live ticker callback. 2000 ms = update every 2 seconds.
            dcc.Interval(id="live-interval", interval=2000, n_intervals=0),
            html.Footer(
                "Book Analytics Pipeline · Lab 13 · Dash + MongoDB + Docker",
                className="text-muted text-center small py-3",
            ),
        ],
        fluid=True,
        className="px-4",
    )
