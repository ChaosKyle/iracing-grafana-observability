#!/bin/bash
# Entrypoint script for the Grafana dashboard container

# Wait for Prometheus and PostgreSQL to be ready
echo "Waiting for databases to be ready..."

MAX_RETRIES=30
RETRY_INTERVAL=5

# Check if Prometheus is available
if [ ! -z "$PROMETHEUS_HOST" ]; then
    echo "Checking Prometheus at $PROMETHEUS_HOST:9090..."
    
    retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if curl -s -f "$PROMETHEUS_HOST:9090/-/healthy" > /dev/null 2>&1; then
            echo "Prometheus is ready!"
            break
        fi
        
        retry_count=$((retry_count+1))
        if [ $retry_count -eq $MAX_RETRIES ]; then
            echo "WARNING: Prometheus health check failed after $MAX_RETRIES attempts. Continuing anyway..."
            break
        fi
        
        echo "Waiting for Prometheus to be ready... (attempt $retry_count/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    done
fi

# Check if PostgreSQL is available
if [ ! -z "$POSTGRES_HOST" ]; then
    echo "Checking PostgreSQL at $POSTGRES_HOST:5432..."
    
    retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if pg_isready -h "$POSTGRES_HOST" -p 5432 -q; then
            echo "PostgreSQL is ready!"
            break
        fi
        
        retry_count=$((retry_count+1))
        if [ $retry_count -eq $MAX_RETRIES ]; then
            echo "WARNING: PostgreSQL health check failed after $MAX_RETRIES attempts. Continuing anyway..."
            break
        fi
        
        echo "Waiting for PostgreSQL to be ready... (attempt $retry_count/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    done
fi

# Update datasource configuration with environment variables
if [ ! -z "$PROMETHEUS_HOST" ]; then
    sed -i "s|http://prometheus:9090|http://${PROMETHEUS_HOST}:9090|g" /etc/grafana/provisioning/datasources/prometheus.yaml
fi

if [ ! -z "$POSTGRES_HOST" ] && [ ! -z "$POSTGRES_PASSWORD" ]; then
    sed -i "s|host: postgres|host: ${POSTGRES_HOST}|g" /etc/grafana/provisioning/datasources/postgres.yaml
    sed -i "s|password: postgres_password|password: ${POSTGRES_PASSWORD}|g" /etc/grafana/provisioning/datasources/postgres.yaml
fi

# Start Grafana
echo "Starting Grafana..."
exec /run.sh