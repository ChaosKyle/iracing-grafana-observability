FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    cron \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy collector code and token helpers
COPY python/collectors/ ./collectors/
COPY python/utils/ ./utils/
COPY python/get_iracing_token.py .
COPY python/auth_strategy.py .
COPY python/iracing_token.json .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy entry point script and token refresh scripts
COPY docker/collector/entrypoint.sh .
COPY docker/collector/refresh_token.sh .
RUN chmod +x entrypoint.sh refresh_token.sh

# Create a non-root user and give proper permissions
RUN useradd -m appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Switch to appuser
USER appuser

# Use explicit shell and path for entrypoint
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]