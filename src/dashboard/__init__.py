"""Dashboard package for the Book Analytics Pipeline (Lab 13).

This package turns the cleaned book dataset (stored in MongoDB, with a
CSV fallback) into a live, interactive Dash web application. It is split
into three focused modules so the root ``app.py`` entry point stays small:

* :mod:`dashboard.data_access` - MongoDB / CSV data loading and filtering.
* :mod:`dashboard.layout`      - the Dash page structure (filters, cards, charts).
* :mod:`dashboard.callbacks`   - the interactive logic that redraws the charts.

The submodules are intentionally **not** imported here so that simply
importing the package has no side effects (loading data, opening DB
connections). ``app.py`` imports exactly what it needs:

    from dashboard.layout import build_layout
    from dashboard.callbacks import register_callbacks
"""

__all__ = ["data_access", "layout", "callbacks"]
