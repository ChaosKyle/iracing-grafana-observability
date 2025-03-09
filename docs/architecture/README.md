# Architecture Overview

## System Architecture

The iRacing Grafana Observability Project is designed with a modular architecture to collect, store, process, and visualize iRacing telemetry and performance data.

### Local Development Architecture

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
                      │  Metrics      │────►│  Dashboards   │
                      │  (Prometheus) │     │  (Local)      │
                      └───────────────┘     └───────────────┘
```

### Cloud Production Architecture

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  iRacing API  │     │ Telemetry     │     │  Race Results │
│  & Telemetry  │◄────┤ Collector     │────►│  Database     │
│               │     │ (Python)      │     │  (PostgreSQL) │
└───────────────┘     └───────┬───────┘     └───────┬───────┘
                              │                     │
                              ▼                     │
                      ┌───────────────┐             │
                      │               │             │
                      │  Prometheus   │             │
                      │  Metrics      │             │
                      │  (Local)      │             │
                      └───────┬───────┘             │
                              │                     │
                              │ remote_write        │
                              ▼                     ▼
                      ┌───────────────────────────────────┐
                      │                                   │
                      │           Grafana Cloud           │
                      │  ┌─────────────┐ ┌─────────────┐  │
                      │  │ Prometheus  │ │ PostgreSQL  │  │
                      │  │ Data Source │ │ Data Source │  │
                      │  └─────────────┘ └─────────────┘  │
                      │           Dashboards              │
                      │                                   │
                      └───────────────────────────────────┘
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
   - Prometheus: Stores time-series metrics for telemetry data with efficient querying

4. **Visualization**
   - Grafana: Provides dashboards for visualization and analysis
   - Custom dashboards organized by category (performance, telemetry, strategy, trends)
   - Two deployment options:
     - Local Grafana instance for development
     - Grafana Cloud for production with enhanced features

5. **Deployment**
   - Docker containers for all components
   - Terraform for infrastructure provisioning
   - GitHub Actions for CI/CD pipelines

## Data Flow

### Local Development Flow

1. The collector authenticates with iRacing API and retrieves race results and driver data
2. Telemetry files are processed and transformed into Prometheus metrics
3. Structured data is stored in PostgreSQL tables with appropriate relations
4. Metrics are exposed via an HTTP endpoint and scraped by Prometheus
5. Local Grafana queries both data sources to render dashboards
6. Users interact with the local Grafana interface to analyze their racing performance

### Cloud Production Flow

1. Same local collection process occurs on the user's machine
2. Telemetry metrics are collected by local Prometheus
3. Prometheus remote_writes metrics to Grafana Cloud Prometheus
4. PostgreSQL data is exposed via port forwarding or cloud DB connection
5. Grafana Cloud dashboards query both data sources
6. Users access Grafana Cloud from any device without needing their local system running

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
- Prometheus for metric storage

### Grafana Cloud Production
- Terraform-managed Grafana Cloud resources
- Local Prometheus with remote_write to Grafana Cloud
- Local PostgreSQL database (with option for cloud DB)
- Metrics visible from any device via Grafana Cloud
- Shared dashboards with team members
- Enhanced performance and reliability

### Self-Hosted Cloud (Alternative)
- Terraform modules for AWS/GCP/Azure deployment
- Managed database services for PostgreSQL
- Managed Prometheus service or self-hosted
- Containerized collector running on schedule
- Self-hosted Grafana service on cloud VMs