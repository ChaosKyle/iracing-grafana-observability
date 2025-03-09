# Deployment Models

This document outlines the different deployment models available for the iRacing Grafana Observability system.

## Development Environment

The development environment is designed for local use and testing:

```
┌───────────────────────────────────────────────────┐
│                Docker Environment                 │
│                                                   │
│  ┌─────────────┐  ┌─────────────┐ ┌─────────────┐ │
│  │             │  │             │ │             │ │
│  │ PostgreSQL  │  │ Prometheus  │ │ Grafana     │ │
│  │ Container   │  │ Container   │ │ Container   │ │
│  │             │  │             │ │             │ │
│  └─────────────┘  └─────────────┘ └─────────────┘ │
│                                                   │
│  ┌─────────────┐                                  │
│  │             │                                  │
│  │ Collector   │                                  │
│  │ Container   │                                  │
│  │             │                                  │
│  └─────────────┘                                  │
└───────────────────────────────────────────────────┘
          ▲
          │ Docker Compose
          │
┌───────────────────────────────────────────────────┐
│                                                   │
│               Local User Machine                  │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Setup Process

1. Clone the repository
2. Create `.env` file with credentials
3. Run `docker-compose up -d`
4. Access Grafana at http://localhost:3000

### Pros and Cons

**Advantages:**
- Simple setup with minimal requirements
- All data contained locally
- No cloud costs
- Direct access to all components

**Disadvantages:**
- Limited to single machine
- Cannot be accessed remotely
- No automatic scaling
- Must keep local machine running to view dashboards

## Grafana Cloud Production Environment

The Grafana Cloud model combines local processing with cloud-based dashboards:

```
┌───────────────────────────────────────────────────┐
│                Local Environment                  │
│                                                   │
│  ┌─────────────┐  ┌─────────────┐                 │
│  │             │  │             │                 │
│  │ PostgreSQL  │  │ Prometheus  │───────┐         │
│  │ Container   │  │ Container   │       │         │
│  │             │  │             │       │         │
│  └─────────────┘  └─────────────┘       │         │
│        │                                │         │
│        │                                │         │
│  ┌─────────────┐           Remote Write │         │
│  │             │                        │         │
│  │ Collector   │                        │         │
│  │ Container   │                        │         │
│  │             │                        │         │
│  └─────────────┘                        │         │
└─────────────────────────────────────────┼─────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────┐
│                 Grafana Cloud                     │
│                                                   │
│  ┌─────────────┐  ┌─────────────┐ ┌─────────────┐ │
│  │             │  │             │ │             │ │
│  │ PostgreSQL  │  │ Prometheus  │ │ Grafana     │ │
│  │ Connection  │  │ Data Source │ │ Dashboards  │ │
│  │             │  │             │ │             │ │
│  └─────────────┘  └─────────────┘ └─────────────┘ │
│                                                   │
└───────────────────────────────────────────────────┘
          ▲
          │ HTTPS
          │
┌───────────────────────────────────────────────────┐
│                                                   │
│         Any Device with Web Browser               │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Setup Process

1. Sign up for Grafana Cloud account
2. Set up local infrastructure with Docker Compose
3. Configure Prometheus remote_write to Grafana Cloud
4. Set up PostgreSQL connection to Grafana Cloud 
5. Deploy dashboards to Grafana Cloud via Terraform

### Pros and Cons

**Advantages:**
- Access dashboards from any device
- Share dashboards with team members
- Professional-grade infrastructure
- Automatic backups
- Advanced alerting capabilities
- No need to keep local system running to view dashboards

**Disadvantages:**
- Requires Grafana Cloud account
- Potential costs for higher data volumes
- Data leaves your local system
- Still requires local collection process

## Self-Hosted Cloud Environment

For full cloud deployment, all components can be hosted in cloud providers:

```
┌───────────────────────────────────────────────────┐
│                 Cloud Provider                    │
│                                                   │
│  ┌─────────────┐  ┌─────────────┐ ┌─────────────┐ │
│  │             │  │             │ │             │ │
│  │ Managed     │  │ Managed     │ │ Self-hosted │ │
│  │ PostgreSQL  │  │ Prometheus  │ │ Grafana     │ │
│  │             │  │             │ │             │ │
│  └─────────────┘  └─────────────┘ └─────────────┘ │
│                                                   │
│  ┌─────────────┐  ┌─────────────┐                 │
│  │             │  │             │                 │
│  │ Serverless  │  │ iRacing API │                 │
│  │ Collector   │◄─┤ Credentials │                 │
│  │             │  │ Vault       │                 │
│  └─────────────┘  └─────────────┘                 │
└───────────────────────────────────────────────────┘
          ▲
          │ HTTPS
          │
┌───────────────────────────────────────────────────┐
│                                                   │
│         Any Device with Web Browser               │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Setup Process

1. Provision cloud infrastructure using Terraform
2. Deploy containerized collector to cloud
3. Set up managed database services
4. Configure Grafana instance in cloud
5. Set up secure credential storage
6. Configure automated collection schedules

### Pros and Cons

**Advantages:**
- Fully cloud-based solution
- No local infrastructure required
- Automatic scaling
- High availability
- Professional infrastructure

**Disadvantages:**
- Highest cost option
- Most complex setup
- Requires cloud expertise
- Need to manage cloud security
- iRacing credentials stored in cloud

## Deployment Selection Guide

| Requirement | Recommended Deployment |
|-------------|------------------------|
| Just getting started | Local Development |
| Sharing with teammates | Grafana Cloud |
| Viewing on mobile devices | Grafana Cloud |
| Minimizing costs | Local Development |
| Enterprise-grade setup | Self-Hosted Cloud |
| Maximum data privacy | Local Development |
| Reliability and uptime | Grafana Cloud or Self-Hosted Cloud |
| Simplest setup | Local Development |