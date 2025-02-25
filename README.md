# iRacing Grafana Observability Project

A comprehensive solution for visualizing iRacing telemetry and performance data using Grafana, managed with Terraform and automated with GitHub Actions.

![iRacing Telemetry Dashboard](docs/images/dashboard-preview.png)

## Overview

This project provides a full-stack solution to collect, store, and visualize iRacing data:

- **Data Collection**: Python scripts to extract data from the iRacing API and telemetry files
- **Storage**: PostgreSQL for historical race data and InfluxDB for time-series telemetry data
- **Visualization**: Grafana dashboards for performance analysis and insights
- **Infrastructure**: Terraform configurations for cloud deployment
- **Containerization**: Docker images for all components
- **Automation**: GitHub Actions workflows for CI/CD

## Project Structure

- `/terraform` - Infrastructure as Code for deploying resources
  - `/modules` - Reusable Terraform modules (Grafana, InfluxDB, PostgreSQL)
  - `/environments` - Environment-specific configurations (dev, prod)
- `/python` - Data extraction and processing scripts
  - `/collectors` - Scripts for collecting data from iRacing API
  - `/processors` - Data transformation and analysis
  - `/utils` - Shared utility functions and database connectors
- `/dashboards` - Grafana dashboard definitions
  - `/performance` - Performance analysis dashboards
  - `/telemetry` - Car telemetry visualizations
  - `/strategy` - Race strategy insights
  - `/trends` - Long-term performance trends
- `/docker` - Docker configurations for containerized deployment
  - `/collector` - Data collector container
  - `/dashboard` - Grafana dashboard container
- `/docs` - Project documentation and guides

## Prerequisites

- iRacing membership and API access
- Docker and Docker Compose
- Terraform (for cloud deployment)
- Python 3.10+
- Git

## Getting Started

### Quick Start with Docker Compose

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/iracing-grafana-observability.git
   cd iracing-grafana-observability
   ```

2. Create a `.env` file with your credentials:
   ```
   IRACING_USERNAME=your_iracing_username
   IRACING_PASSWORD=your_iracing_password
   POSTGRES_PASSWORD=secure_password
   INFLUXDB_ADMIN_PASSWORD=secure_password
   ```

3. Launch the stack:
   ```bash
   docker-compose up -d
   ```

4. Access Grafana at http://localhost:3000 (default credentials: admin/admin)

### Local Development Setup

1. Set up environment variables for iRacing API access:
   ```bash
   cp docker/collector/config.env .env
   # Edit .env with your credentials
   ```

2. Initialize local environment:
   ```bash
   ./setup.sh
   ```

3. Activate Python virtual environment:
   ```bash
   source venv/bin/activate
   ```

4. Run data collector:
   ```bash
   python python/collectors/iracing_collector.py
   ```

## Cloud Deployment with Terraform

1. Navigate to the environment directory:
   ```bash
   cd terraform/environments/dev
   ```

2. Create a `terraform.tfvars` file:
   ```
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your credentials
   ```

3. Initialize and apply Terraform configuration:
   ```bash
   terraform init
   terraform apply
   ```

## Dashboard Features

- **Performance Analysis**: Track your iRating, Safety Rating, and race results over time
- **Telemetry Visualization**: Analyze car performance data including speed, throttle, brake, and more
- **Race Strategy**: Fuel consumption, pit stop optimization, and consistency analysis
- **Track Insights**: Compare performance across different tracks and car setups

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and run tests
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin feature/my-feature`
6. Submit a pull request

## License

MIT

## Acknowledgements

- [iRacing](https://www.iracing.com/) for their simulator and API
- [Grafana](https://grafana.com/) for the visualization platform
- [InfluxDB](https://www.influxdata.com/) for time-series data storage
- [PostgreSQL](https://www.postgresql.org/) for relational data storage
- [pyRacing](https://github.com/Esterni/pyracing) for Python iRacing API client