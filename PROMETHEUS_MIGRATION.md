# Migration from InfluxDB to Prometheus

This document outlines the changes made to convert the iRacing Grafana Observability project from using InfluxDB to Prometheus for time-series metrics storage.

## Why Prometheus?

- Prometheus is natively supported by Grafana with excellent integration
- Simpler configuration without tokens and complex authentication
- Better performance for metrics-based data
- More straightforward dashboarding experience in Grafana

## Changes Made

### Docker Compose

- Replaced InfluxDB container with Prometheus container
- Updated environment variables to use Prometheus settings
- Added port 8000 to expose metrics endpoint on the collector
- Updated dependencies between services

### Prometheus Configuration

- Added new `docker/prometheus` directory
- Created `prometheus.yml` with scrape configuration
- Set up Prometheus to scrape metrics from the collector service

### Grafana Configuration

- Updated datasource configuration to use Prometheus
- Renamed configuration files
- Modified provisioning scripts and entrypoint to handle Prometheus

### Python Collector

- Created new `prometheus_connector.py` to replace `influx_connector.py`
- Updated collector to expose metrics via HTTP endpoint
- Enhanced collector to run continuously as a service
- Updated dependencies to include Prometheus client

## How to Use

1. Make sure to run `docker-compose down` to stop any existing containers
2. The new Prometheus configuration will automatically be used when you run `docker-compose up -d`
3. Grafana dashboards will be provisioned with Prometheus as a datasource
4. Metrics will be exposed from the collector and scraped by Prometheus

## Verifying the Setup

1. Access Prometheus UI at http://localhost:9090
2. Access Grafana at http://localhost:3000 (default credentials: admin/admin)
3. Verify that Prometheus datasource is working in Grafana by checking the datasource connection
4. Check for metrics at http://localhost:8000/metrics (from the collector)

## Additional Benefits

- Easier to add metrics to the collector
- Centralized metrics management with default retention policy
- Better querying capabilities with PromQL
- Simpler debugging experience