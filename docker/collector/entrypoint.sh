#!/bin/bash
# Entrypoint script for the iRacing collector container

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

# Create a .env file based on environment variables
env | grep -E '^(IRACING_|POSTGRES_|PROMETHEUS_)' > .env

echo "Starting iRacing data collector with Prometheus metrics endpoint..."

# Run the iRacing collector with the Prometheus version
# This will start the HTTP server for metrics and keeps running
python collectors/iracing_collector_prometheus.py

# Note: We don't use cron here because the Prometheus collector
# needs to keep running to serve metrics to Prometheus.
# Instead, we can set up a periodic collection via the code itself.