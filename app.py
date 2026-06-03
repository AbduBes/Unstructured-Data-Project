"""Main Dash entry point for the Book Analytics dashboard (Lab 13).

This file is intentionally thin: it creates the Dash app, applies a Bootstrap
theme, attaches the layout from :mod:`dashboard.layout`, registers every
callback from :mod:`dashboard.callbacks`, and exposes the underlying Flask
server so Gunicorn can serve it in production.

Run locally:
    python app.py
    # then open http://127.0.0.1:8050

Run in production (inside the Docker image):
    gunicorn app:server --bind 0.0.0.0:8050 --workers 2
"""

import os
import sys
from pathlib import Path

# Make the ``src`` folder importable so ``import dashboard`` works without
# installing the project as a package.
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import dash
import dash_bootstrap_components as dbc

from dashboard.callbacks import register_callbacks
from dashboard.layout import build_layout

# --------------------------------------------------------------------------- #
# Application object
# --------------------------------------------------------------------------- #
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Book Analytics",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# Expose the WSGI server for Gunicorn: ``gunicorn app:server``.
server = app.server

# Build the page and wire up the interactivity.
app.layout = build_layout()
register_callbacks(app)


if __name__ == "__main__":
    # Development server. debug=True enables hot-reload; never use it in prod.
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)
