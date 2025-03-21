# Terraform Infrastructure Documentation

This document explains the Terraform configuration for the iRacing Grafana Observability project.

## Directory Structure

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf         # Main configuration for dev environment
│   │   ├── outputs.tf      # Output values from the dev environment
│   │   ├── terraform.tfvars.example  # Example variables file
│   │   └── variables.tf    # Variable declarations for dev environment
│   └── prod/
│       ├── main.tf         # Main configuration for production environment (Grafana Cloud)
│       ├── outputs.tf      # Output values from the production environment
│       ├── terraform.tfvars.example  # Example variables file
│       └── variables.tf    # Variable declarations for production environment
└── modules/
    ├── grafana/            # Local Grafana module
    │   ├── dashboards/     # JSON dashboard definitions
    │   ├── main.tf         # Grafana resources configuration
    │   ├── outputs.tf      # Grafana module outputs
    │   └── variables.tf    # Grafana module variables
    ├── grafana_cloud/      # Grafana Cloud module
    │   ├── dashboards/     # JSON dashboard definitions (linked from grafana module)
    │   ├── main.tf         # Grafana Cloud resources configuration
    │   ├── outputs.tf      # Grafana Cloud module outputs
    │   └── variables.tf    # Grafana Cloud module variables
    ├── prometheus/         # Prometheus module
    │   ├── main.tf         # Prometheus resources configuration
    │   ├── outputs.tf      # Prometheus module outputs
    │   └── variables.tf    # Prometheus module variables
    └── postgres/           # PostgreSQL module
        ├── main.tf         # PostgreSQL resources configuration
        ├── outputs.tf      # PostgreSQL module outputs
        ├── schema.sql      # Database schema definition
        └── variables.tf    # PostgreSQL module variables
```

## Environments

### Development Environment

The development environment (`environments/dev`) is designed for local development and testing. It includes:

- Local Grafana instance running in Docker
- Local Prometheus instance for metrics collection
- Local PostgreSQL database for structured data

### Production Environment (Grafana Cloud)

The production environment (`environments/prod`) is designed for cloud deployment using Grafana Cloud. It includes:

- Grafana Cloud instance for dashboards and visualization
- Local Prometheus instance that remote_writes to Grafana Cloud Metrics
- Local PostgreSQL database (can be replaced with a cloud database)

## Changes Made

### InfluxDB to Prometheus Migration

This Terraform configuration has been updated to replace InfluxDB with Prometheus. The key changes include:

1. Removed the InfluxDB module
2. Added a new Prometheus module
3. Updated the Grafana module to use Prometheus instead of InfluxDB
4. Updated environment variables

### Grafana Cloud Integration

Added support for Grafana Cloud deployment:

1. Created a new `grafana_cloud` module for managing Grafana Cloud resources
2. Added a new production environment that uses Grafana Cloud
3. Updated the Prometheus module to support remote_write to Grafana Cloud
4. Kept the same dashboards between local and cloud environments

## Modules Overview

### Grafana Module

This module sets up local Grafana dashboards and data sources for iRacing telemetry and performance monitoring.

**Key Resources**:
- Grafana folders for organizing dashboards by category
- Data source configurations for Prometheus and PostgreSQL
- Pre-configured dashboards for lap times, car telemetry, race strategy, and performance trends

### Grafana Cloud Module

This module manages Grafana Cloud resources, including dashboards, data sources, and API tokens.

**Key Resources**:
- Grafana folders in Grafana Cloud
- Remote data source configurations
- Same dashboards as the local Grafana instance
- API key creation and management for metrics publishing

### Prometheus Module

This module deploys Prometheus as a Docker container for time-series metrics collection.

**Key Resources**:
- Docker image and container configurations for Prometheus
- Configuration file for Prometheus scrapers
- Remote_write configuration for Grafana Cloud (in production)
- Volume configuration for persistent storage

### PostgreSQL Module

This module deploys PostgreSQL as a Docker container for structured data storage, used for race results, driver statistics, and other relational data.

**Key Resources**:
- Docker image and container configurations for PostgreSQL
- Environment variables for database initialization
- Volume configuration for persistent storage
- Database schema initialization script

## Provider Issues Fixed

The Terraform configuration now correctly specifies provider dependencies in each module to ensure proper provider inheritance. Each module has a `required_providers` block that explicitly declares which provider sources it needs.

## Usage

1. Navigate to the environment directory: `cd terraform/environments/dev`
2. Copy the example vars file: `cp terraform.tfvars.example terraform.tfvars`
3. Edit the `terraform.tfvars` file with your configuration values
4. Initialize Terraform: `terraform init`
5. Apply the configuration: `terraform apply`

## Variables and Customization

Key variables that can be customized include:

- **Grafana**: URLs, admin credentials, and UI settings
- **Prometheus**: Data path and port settings
- **PostgreSQL**: User credentials, database name, and connection settings

Refer to each module's `variables.tf` file for a complete list of configurable options.