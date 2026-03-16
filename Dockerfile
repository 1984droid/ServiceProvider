# Multi-stage Dockerfile for Service Provider Application
# Python 3.14+ with PostgreSQL 18+ support

# Stage 1: Frontend Builder
FROM node:22-slim as frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend for production
RUN npm run build


# Stage 2: Python Builder
FROM python:3.14-slim as python-builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt gunicorn whitenoise


# Stage 3: Runtime
FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from python builder
COPY --from=python-builder /opt/venv /opt/venv

# Create app user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/staticfiles /app/media /app/logs && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy application code (excluding frontend source)
COPY --chown=appuser:appuser --exclude=frontend . .

# Copy built frontend from frontend builder
COPY --from=frontend-builder --chown=appuser:appuser /frontend/dist /app/frontend/dist

# Switch to app user
USER appuser

# Collect static files (includes built frontend)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8100/admin/', timeout=5)"

# Default command
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8100", "--workers", "4", "--timeout", "120"]
