# Multi-stage build for Django backend
FROM python:3.13-slim AS base

USER root

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=area_project.settings

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies (production only)
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy entrypoint script and make it executable
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/mediafiles /app/logs

# Make manage.py executable
RUN chmod +x /app/manage.py

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=10s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8080/health/ || exit 1

# Default command - ASGI with UvicornWorker for WebSocket support
ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8080 --workers ${GUNICORN_WORKERS:-3} --worker-class uvicorn.workers.UvicornWorker --timeout 60 --forwarded-allow-ips='*' --access-logfile - --error-logfile - area_project.asgi:application"]