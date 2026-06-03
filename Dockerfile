# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Dockerfile for the Book Analytics dashboard (Lab 13)
#
# Builds a small, reproducible image that serves the Dash app with Gunicorn
# (a production WSGI server) instead of the Flask development server.
# ---------------------------------------------------------------------------
FROM python:3.12-slim

# Keep Python output unbuffered and skip .pyc files for a cleaner container.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so this layer is cached across code changes.
# We use the lean dashboard requirements rather than the full project file
# (which contains heavy ML/Jupyter packages the dashboard doesn't need).
COPY requirements-dashboard.txt ./
RUN pip install --no-cache-dir -r requirements-dashboard.txt

# Copy the application code (the .dockerignore keeps the context lean).
COPY . .

# Dash/Gunicorn listen on 8050.
EXPOSE 8050

# Production server. ``app:server`` is the Flask WSGI object exposed in app.py.
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:8050", "--workers", "2", "--threads", "2", "--timeout", "120"]
