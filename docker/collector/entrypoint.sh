#!/bin/bash
# Entrypoint script for the iRacing collector container

# Check for required environment variables
if [ -z "$IRACING_USERNAME" ] || [ -z "$IRACING_PASSWORD" ]; then
    echo "ERROR: IRACING_USERNAME and IRACING_PASSWORD environment variables must be set"
    exit 1
fi

# Check for database credentials
if [ -z "$POSTGRES_HOST" ] || [ -z "$INFLUXDB_URL" ] || [ -z "$INFLUXDB_TOKEN" ]; then
    echo "ERROR: Database connection environment variables must be set"
    echo "Required: POSTGRES_HOST, INFLUXDB_URL, INFLUXDB_TOKEN"
    exit 1
fi

# Create a .env file based on environment variables
env | grep -E '^(IRACING_|POSTGRES_|INFLUXDB_)' > .env

echo "Starting iRacing data collector..."

# Run the iRacing collector
python collectors/iracing_collector.py

# If a cron schedule is provided, set up cron
if [ ! -z "$COLLECTOR_CRON_SCHEDULE" ]; then
    echo "Setting up cron job with schedule: $COLLECTOR_CRON_SCHEDULE"
    
    # Install cron if not already installed
    if ! command -v cron &> /dev/null; then
        apt-get update && apt-get install -y cron
    fi
    
    # Create cron job
    echo "$COLLECTOR_CRON_SCHEDULE python /app/collectors/iracing_collector.py >> /app/collector.log 2>&1" > /tmp/crontab
    crontab /tmp/crontab
    rm /tmp/crontab
    
    # Start cron in foreground
    echo "Starting cron service..."
    cron -f
fi