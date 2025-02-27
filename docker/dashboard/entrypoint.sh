#!/bin/bash
# Entrypoint script for the Grafana dashboard container

# Wait for InfluxDB and PostgreSQL to be ready
echo "Waiting for databases to be ready..."

MAX_RETRIES=30
RETRY_INTERVAL=5

# Check if InfluxDB is available
if [ ! -z "$INFLUXDB_HOST" ]; then
    echo "Checking InfluxDB at $INFLUXDB_HOST:8086..."
    
    retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if curl -s -f "$INFLUXDB_HOST:8086/health" > /dev/null 2>&1 || curl -s -f "$INFLUXDB_HOST:8086/ping" > /dev/null 2>&1; then
            echo "InfluxDB is ready!"
            break
        fi
        
        retry_count=$((retry_count+1))
        if [ $retry_count -eq $MAX_RETRIES ]; then
            echo "WARNING: InfluxDB health check failed after $MAX_RETRIES attempts. Continuing anyway..."
            break
        fi
        
        echo "Waiting for InfluxDB to be ready... (attempt $retry_count/$MAX_RETRIES)"
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
if [ ! -z "$INFLUXDB_HOST" ] && [ ! -z "$INFLUXDB_TOKEN" ]; then
    sed -i "s|http://influxdb:8086|http://${INFLUXDB_HOST}:8086|g" /etc/grafana/provisioning/datasources/influxdb.yaml
    sed -i "s|TOKEN_PLACEHOLDER|${INFLUXDB_TOKEN}|g" /etc/grafana/provisioning/datasources/influxdb.yaml
fi

if [ ! -z "$POSTGRES_HOST" ] && [ ! -z "$POSTGRES_PASSWORD" ]; then
    sed -i "s|host: postgres|host: ${POSTGRES_HOST}|g" /etc/grafana/provisioning/datasources/postgres.yaml
    sed -i "s|password: postgres_password|password: ${POSTGRES_PASSWORD}|g" /etc/grafana/provisioning/datasources/postgres.yaml
fi

# Start Grafana
echo "Starting Grafana..."
exec /run.sh