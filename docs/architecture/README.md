# Architecture Overview

## System Architecture

The iRacing Grafana Observability Project is designed with a modular architecture to collect, store, process, and visualize iRacing telemetry and performance data.

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  iRacing API  │     │ Telemetry     │     │  Race Results │
│  & Telemetry  │◄────┤ Collector     │────►│  Database     │
│               │     │ (Python)      │     │  (PostgreSQL) │
└───────────────┘     └───────┬───────┘     └───────┬───────┘
                              │                     │
                              ▼                     ▼
                      ┌───────────────┐     ┌───────────────┐
                      │               │     │               │
                      │  Time-Series  │     │  Grafana      │
                      │  Database     │────►│  Dashboards   │
                      │  (InfluxDB)   │     │               │
                      └───────────────┘     └───────────────┘
```

## Component Breakdown

1. **Data Sources**
   - iRacing API: Provides access to race results, career stats, and session information
   - Telemetry Files: Direct telemetry data from iRacing sessions (.ibt files)

2. **Data Collection**
   - Python collector scripts to extract and process data
   - Scheduled collection via cron jobs or GitHub Actions
   - Authentication with iRacing credentials

3. **Data Storage**
   - PostgreSQL: Stores structured data like race results, driver profiles, and track information
   - InfluxDB: Stores time-series telemetry data for high-performance querying

4. **Visualization**
   - Grafana: Provides dashboards for visualization and analysis
   - Custom dashboards organized by category (performance, telemetry, strategy, trends)

5. **Deployment**
   - Docker containers for all components
   - Terraform for infrastructure provisioning
   - GitHub Actions for CI/CD pipelines

## Data Flow

1. The collector authenticates with iRacing API and retrieves race results and driver data
2. Telemetry files are processed and transformed into time-series data points
3. Structured data is stored in PostgreSQL tables with appropriate relations
4. Time-series telemetry data is stored in InfluxDB buckets
5. Grafana queries both data sources to render dashboards and visualizations
6. Users interact with the Grafana interface to analyze their racing performance

## Security Considerations

- iRacing credentials are stored as secure environment variables
- Database credentials are managed securely in Terraform variables
- No sensitive data is committed to the repository
- Container security best practices are followed
- All connections use TLS/SSL when deployed in production

## Deployment Options

### Local Development
- Docker Compose for local stack deployment
- Direct Python script execution
- Local Grafana instance

### Cloud Deployment
- Terraform modules for AWS/GCP/Azure deployment
- Managed database services for PostgreSQL and InfluxDB
- Containerized collector running on schedule
- Hosted Grafana service or self-hosted on cloud VMs