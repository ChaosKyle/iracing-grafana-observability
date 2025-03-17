#!/bin/bash
# Entrypoint script for the iRacing collector container with token management

# Check for required environment variables
if [ -z "$IRACING_USERNAME" ] || [ -z "$IRACING_PASSWORD" ]; then
    echo "ERROR: IRACING_USERNAME and IRACING_PASSWORD environment variables must be set"
    exit 1
fi

# Check for database credentials
if [ -z "$POSTGRES_HOST" ] || [ -z "$PROMETHEUS_HOST" ]; then
    echo "ERROR: Database connection environment variables must be set"
    echo "Required: POSTGRES_HOST, PROMETHEUS_HOST"
    exit 1
fi

# Set token refresh schedule based on environment variable or default to daily
TOKEN_REFRESH_SCHEDULE=${TOKEN_REFRESH_SCHEDULE:-"0 0 * * *"}
TOKEN_REFRESH_SCRIPT="/app/refresh_token.sh"

echo "Setting up token refresh cron job: $TOKEN_REFRESH_SCHEDULE"

# Create cron job for token refresh
echo "$TOKEN_REFRESH_SCHEDULE $TOKEN_REFRESH_SCRIPT > /proc/1/fd/1 2>&1" > /tmp/token_cron
crontab /tmp/token_cron
rm /tmp/token_cron

# Start cron service in background
service cron start

# Run initial token check and refresh if needed
echo "Performing initial token check..."
bash $TOKEN_REFRESH_SCRIPT

# Override iracing_token.json with an environment variable if provided
if [ ! -z "$IRACING_TOKEN" ]; then
    echo "Using token from IRACING_TOKEN environment variable"
    echo "$IRACING_TOKEN" > /app/iracing_token.json
    chmod 600 /app/iracing_token.json
fi

# Initialize AUTH_STRATEGY environment variable
# Options: api_direct, token_file, cookie
export AUTH_STRATEGY=${AUTH_STRATEGY:-"token_file"}
echo "Using auth strategy: $AUTH_STRATEGY"

echo "Starting iRacing data collector with Prometheus metrics endpoint..."

# Run the iRacing collector with the Prometheus version
# This will start the HTTP server for metrics and keeps running
python collectors/iracing_collector_prometheus.py

# Note: We don't use cron here because the Prometheus collector
# needs to keep running to serve metrics to Prometheus.
# Instead, we can set up a periodic collection via the code itself.