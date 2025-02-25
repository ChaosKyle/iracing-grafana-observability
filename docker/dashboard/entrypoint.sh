#!/bin/bash
# Entrypoint script for the Grafana dashboard container

# Wait for InfluxDB and PostgreSQL to be ready
echo "Waiting for databases to be ready..."

if [ ! -z "$INFLUXDB_HOST" ]; then
    until curl -s "$INFLUXDB_HOST:8086/health" | grep -q "ready"; do
        echo "Waiting for InfluxDB to be ready..."
        sleep 5
    done
    echo "InfluxDB is ready!"
fi

if [ ! -z "$POSTGRES_HOST" ]; then
    until pg_isready -h "$POSTGRES_HOST" -p 5432; do
        echo "Waiting for PostgreSQL to be ready..."
        sleep 5
    done
    echo "PostgreSQL is ready!"
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