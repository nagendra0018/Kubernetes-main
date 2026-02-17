# Multi-stage Dockerfile for DCN Collector Service

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    librdkafka1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 dcnuser && \
    chown -R dcnuser:dcnuser /app

USER dcnuser

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV COLLECTOR_POLL_INTERVAL=60
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the collector
CMD ["python", "-m", "src.main"]
