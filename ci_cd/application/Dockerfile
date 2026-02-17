# Production Dockerfile for Flask Application

# Stage 1: Build Stage
FROM python:3.11-slim AS builder

WORKDIR /build

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production Stage
FROM python:3.11-slim

LABEL maintainer="devops@example.com"
LABEL app="cicd-demo"
LABEL environment="production"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    PORT=8000 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "src.app:app"]
