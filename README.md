# iRacing Grafana Observability

A comprehensive solution for collecting, storing, and visualizing iRacing telemetry and performance data using Grafana, managed with Terraform and automated with GitHub Actions.

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

```
.
├── .github/                    # GitHub Actions workflows and variables
│   ├── workflows/              # CI/CD workflow definitions
│   └── variables.yaml          # Centralized variable definitions
├── docker/                     # Docker configurations
│   ├── collector/              # Data collector container
│   └── dashboard/              # Grafana dashboard container
├── docs/                       # Documentation and guides
│   ├── architecture/           # System architecture documentation
│   └── blog/                   # Guides and blog posts
├── python/                     # Python code
│   ├── collectors/             # Data collection scripts
│   ├── tests/                  # Unit and integration tests
│   └── utils/                  # Utility functions and connectors
├── terraform/                  # Infrastructure as Code
│   ├── environments/           # Environment configurations
│   └── modules/                # Reusable Terraform modules
│       ├── grafana/            # Grafana module with dashboards
│       ├── influxdb/           # InfluxDB time-series database
│       └── postgres/           # PostgreSQL relational database
├── README.md                   # Project documentation
├── docker-compose.yml          # Local development stack
└── setup.sh                    # Setup script for local development
```

## Prerequisites

- iRacing membership and API access
- Docker and Docker Compose
- Terraform v1.0+ (for cloud deployment)
- Python 3.10+
- Git

## Setup and Installation

### Quick Start with Docker Compose

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ChaosKyle/iracing-grafana-observability.git
   cd iracing-grafana-observability
   ```

2. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```bash
   # iRacing Credentials
   IRACING_USERNAME=your_iracing_username
   IRACING_PASSWORD=your_iracing_password
   
   # Database Credentials
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_DB=iracing_data
   
   # InfluxDB Configuration
   INFLUXDB_URL=http://influxdb:8086
   INFLUXDB_TOKEN=your_influxdb_token
   INFLUXDB_ORG=iracing
   INFLUXDB_BUCKET=iracing_telemetry
   INFLUXDB_ADMIN_USER=admin
   INFLUXDB_ADMIN_PASSWORD=your_secure_password
   ```

3. **Start the stack**:
   ```bash
   docker-compose up -d
   ```

4. **Access Grafana**:
   Open http://localhost:3000 in your browser
   - Default credentials: admin/admin
   - You'll be prompted to change the password on first login

### Local Development Setup

1. **Set up the Python environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r python/requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

4. **Run the data collector**:
   ```bash
   python python/collectors/iracing_collector.py
   ```

## Cloud Deployment with Terraform

1. **Configure cloud provider credentials**:
   Set up your cloud provider credentials according to Terraform's documentation for your chosen provider (AWS, Azure, GCP).

2. **Set up Terraform variables**:
   ```bash
   cd terraform/environments/dev
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your configuration
   ```

3. **Initialize and deploy**:
   ```bash
   terraform init
   terraform plan  # Review the changes
   terraform apply  # Deploy the infrastructure
   ```

4. **Get output information**:
   ```bash
   terraform output  # Shows URLs and connection details
   ```

## GitHub Actions Workflows

The project includes automated CI/CD pipelines using GitHub Actions:

1. **Python CI**: Runs tests and linting for Python code changes
   - Triggers on changes to Python files
   - Runs flake8 and pytest

2. **Docker Build & Push**: Builds and publishes Docker images to GitHub Container Registry
   - Triggers on changes to Dockerfile or related files
   - Builds collector and dashboard images

3. **Dashboard Validator**: Validates the Grafana dashboard JSON files
   - Checks for proper structure and unique IDs
   - Ensures all dashboards match our standards

4. **Data Collection**: Scheduled workflow to collect data from iRacing
   - Runs every 6 hours
   - Can be triggered manually via workflow_dispatch

### Workflow Customization

Workflow settings are centralized in `.github/variables.yaml`, making it easy to adjust parameters across all workflows from a single file.

## Dashboard Features

- **Performance Analysis**: Track your iRating, Safety Rating, and race results over time
- **Telemetry Visualization**: Analyze car performance data including speed, throttle, brake, etc.
- **Race Strategy**: Fuel consumption, pit stop optimization, and consistency analysis
- **Track Insights**: Compare performance across different tracks and car setups

## Available Dashboards

The project includes the following Grafana dashboards:

1. **Car Telemetry**: Real-time and historical car performance data
2. **Lap Times**: Detailed lap time analysis with comparisons
3. **Performance Trends**: Long-term iRating and Safety Rating progression
4. **Race Strategy**: Fuel usage, pit stop timing, and race planning tools

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and run tests
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin feature/my-feature`
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines for Python code
- Add unit tests for new functionality
- Update documentation for new features
- Validate dashboards using the dashboard validator script

## Troubleshooting

### Common Issues

1. **Data Collection Errors**:
   - Check iRacing credentials in environment variables
   - Verify network connectivity to iRacing servers
   - Check the logs: `docker-compose logs collector`

2. **Database Connection Issues**:
   - Ensure database containers are running: `docker-compose ps`
   - Verify database credentials in environment variables
   - Check database logs: `docker-compose logs postgres influxdb`

3. **Dashboard Not Loading Data**:
   - Verify data source configuration in Grafana
   - Check that data collection has run successfully
   - Examine Grafana logs: `docker-compose logs dashboard`

## License

MIT

## Acknowledgements

- [iRacing](https://www.iracing.com/) for their simulator and API
- [Grafana](https://grafana.com/) for the visualization platform
- [InfluxDB](https://www.influxdata.com/) for time-series data storage
- [PostgreSQL](https://www.postgresql.org/) for relational data storage
- [pyRacing](https://github.com/Esterni/pyracing) for Python iRacing API client
- [irsdk](https://github.com/kutu/pyirsdk) for iRacing telemetry access