# iRacing Grafana Observability

A comprehensive solution for collecting, storing, and visualizing iRacing telemetry and performance data using Grafana. Supports both local Docker deployment and Grafana Cloud for production use.

![iRacing Telemetry Dashboard]<putapicherewhenyougetitworking>

## Overview

This project provides a full-stack solution to collect, store, and visualize iRacing data:

- **Data Collection**: Python scripts to extract data from the iRacing API and telemetry files
- **Storage**: PostgreSQL for historical race data and Prometheus for time-series telemetry data
- **Visualization**: Grafana dashboards for performance analysis and insights
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
├── terraform/                  # Dashboard definitions and templates
│   └── modules/                
│       └── grafana/            # Grafana dashboards
│           └── dashboards/     # Dashboard JSON files
├── README.md                   # Project documentation
├── docker-compose.yml          # Local development stack
└── setup.sh                    # Setup script for local development
```

## Prerequisites

- iRacing membership and API access
- Docker and Docker Compose
  - Mac: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- Python 3.10+
  - Mac: Available via Homebrew or [python.org](https://www.python.org/downloads/macos/)
  - Windows: Available from [python.org](https://www.python.org/downloads/windows/)
- Git
  - Mac: Included with Xcode Command Line Tools or via Homebrew
  - Windows: [Git for Windows](https://gitforwindows.org/)

## Setup and Installation

This project offers two deployment options:
- **Local Development**: For testing and development on your own machine using Docker
- **Grafana Cloud**: For production use with professional monitoring and dashboards

### Local Development Setup with Docker Compose

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
   
   # Prometheus Configuration
   PROMETHEUS_HOST=prometheus
   PROMETHEUS_PORT=9090
   ```

3. **Start the stack**:
   ```bash
   docker-compose up -d
   ```

4. **Access Grafana**:
   Open http://localhost:3000 in your browser (or the port configured in your `.env` file if different)
   - Default credentials: admin/admin
   - You'll be prompted to change the password on first login

### Grafana Cloud Production Setup

For a more robust solution with better performance, uptime, and sharing capabilities, follow these steps to set up a Grafana Cloud environment:

1. **Sign up for Grafana Cloud**:
   - Go to [Grafana Cloud](https://grafana.com/products/cloud/) and sign up for a free account
   - For hobby use, the free tier includes 10K metrics and 50GB logs, which is enough for personal iRacing data

2. **Create a Grafana Cloud Stack**:
   - In the Grafana Cloud portal, create a new stack (or use the default one)
   - Note your stack name/slug (e.g., "my-iracing-data")

3. **Get your Grafana Cloud API keys**:
   - Navigate to your stack
   - Go to "Security" → "API Keys"
   - Create a new API key with Admin role (for Terraform to manage resources)
   - Note this API key as your `grafana_cloud_api_key`
   - Create another API key with Editor role for metrics publishing
   - Note this key as your `grafana_metrics_api_key`

4. **Get your organization ID**:
   - In Grafana Cloud portal, go to your user profile
   - Look for Organization ID in your organization settings
   - Note this as your `grafana_cloud_org_id`

5. **Configure Terraform variables**:
   ```bash
   cd terraform/environments/prod
   cp terraform.tfvars.example terraform.tfvars
   ```
   
6. **Edit the terraform.tfvars file with your Grafana Cloud information**:
   ```
   # Grafana Cloud settings
   grafana_cloud_url = "https://your-stack-slug.grafana.net"
   grafana_cloud_api_key = "your-grafana-cloud-api-key"
   grafana_cloud_org_id = "your-org-id"
   stack_slug = "your-stack-slug"
   grafana_admin_user = "admin"
   grafana_admin_pass = "strong-password"
   
   # Metrics publishing
   grafana_metrics_publisher_id = "your-metrics-publisher-id"
   grafana_metrics_api_key = "your-metrics-api-key"
   
   # Other settings can use the defaults
   ```

7. **Initialize and apply Terraform configuration**:
   ```bash
   terraform init
   terraform apply
   ```
   
   This will:
   - Set up Grafana Cloud dashboards
   - Configure your local Prometheus to remote_write to Grafana Cloud
   - Create necessary API tokens

8. **Start your local stack**:
   ```bash
   cd ../../..  # Back to project root
   docker-compose up -d
   ```

9. **Access your Grafana Cloud instance**:
   - Open your stack URL (e.g., https://your-stack-slug.grafana.net)
   - Log in with your Grafana Cloud credentials
   - Your dashboards should be automatically provisioned

10. **Verify data flow**:
    - Start the collector on your local machine
    - Data should begin flowing to both your local Grafana and Grafana Cloud
    - Check the Prometheus data source in Grafana Cloud to confirm it's receiving data

### Local Development Setup

#### macOS/Linux

1. **Set up the Python environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   source venv/bin/activate
   
   # Install dependencies
   pip install -r python/requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   # Make sure to set POSTGRES_HOST=localhost and PROMETHEUS_HOST=localhost
   ```

3. **Run the setup script**:
   ```bash
   # Make the script executable
   chmod +x setup.sh
   
   # Run the script
   ./setup.sh
   ```

4. **Run the data collector**:
   ```bash
   python python/collectors/iracing_collector_prometheus.py
   ```

#### Windows

1. **Set up the Python environment**:
   ```cmd
   # Create virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r python/requirements.txt
   ```

2. **Configure environment variables**:
   ```cmd
   copy .env.example .env
   # Edit .env with your credentials using Notepad or other text editor
   # Make sure to set POSTGRES_HOST=localhost and PROMETHEUS_HOST=localhost
   ```

3. **Run the setup script**:
   ```cmd
   # If using PowerShell:
   .\setup.ps1
   
   # If using Git Bash:
   ./setup.sh
   ```

4. **Run the data collector**:
   ```cmd
   python python\collectors\iracing_collector_prometheus.py
   ```

## GitHub Actions Workflows

The project includes automated CI/CD pipelines for development:

1. **Python CI**: Runs tests and linting for Python code changes
   - Validates code quality
   - Runs flake8 and pytest

2. **Docker Build**: Builds Docker images
   - Validates Docker configurations
   - Tests container builds

3. **Dashboard Validator**: Validates the Grafana dashboard JSON files
   - Checks for proper structure and unique IDs
   - Ensures all dashboards match our standards

### Workflow Customization

Workflow settings are centralized in `.github/variables.yaml`, making it easy to adjust parameters across all workflows from a single file.

## Dashboard Features

- **Performance Analysis**: Track your iRating, Safety Rating, and race results over time
- **Telemetry Visualization**: Analyze car performance data including speed, throttle, brake, etc.
- **Race Strategy**: Fuel consumption, pit stop optimization, and consistency analysis
- **Track Insights**: Compare performance across different tracks and car setups

## Available Dashboards

The project includes the following Grafana dashboards in both local and cloud environments:

1. **Car Telemetry**: Real-time and historical car performance data
2. **Lap Times**: Detailed lap time analysis with comparisons
3. **Performance Trends**: Long-term iRating and Safety Rating progression
4. **Race Strategy**: Fuel usage, pit stop timing, and race planning tools

## Deployment Options

### Local Development (Docker)

- Quick to set up on your own machine
- Great for testing and personal use
- All data stays on your computer
- Limited sharing capabilities
- Requires Docker running at all times to access data

### Grafana Cloud (Recommended for Sharing)

- Professional-grade infrastructure
- Always available from any device
- Easy to share dashboards with teammates
- Free tier available for hobby use
- Better performance and reliability
- Remote write from local Prometheus for data collection
- Automatic backups of your data

## Metrics Architecture (Prometheus)

This project uses Prometheus for time-series metrics storage, which provides several advantages:

- **Native Grafana Integration**: Prometheus is natively supported by Grafana with built-in query editors
- **Simple Configuration**: No complex token or authentication setup required
- **Pull-Based Model**: Prometheus scrapes metrics from the collector, simplifying the architecture
- **Powerful Query Language**: PromQL offers flexible and powerful querying capabilities

### How Metrics Flow:

1. The collector exposes metrics via an HTTP endpoint (`:8000/metrics`)
2. Prometheus scrapes these metrics at regular intervals (every 15s by default)
3. Grafana queries Prometheus for visualization

### Metric Types:

- **Counter**: Cumulative values that only increase (e.g., total laps completed)
- **Gauge**: Values that can go up and down (e.g., current speed, RPM)
- **Histogram**: Distribution of values (e.g., lap time distributions)

To explore raw metrics, visit `http://localhost:8000/metrics` when the collector is running.

## Usage Guide

### Collecting iRacing Data

#### macOS/Linux

1. **Manual Collection**:
   ```bash
   # Activate your virtual environment if using local setup
   source venv/bin/activate
   
   # Run the collector script
   python python/collectors/iracing_collector_prometheus.py
   ```

2. **Using Docker**:
   ```bash
   # Trigger the collector container
   docker-compose restart collector
   
   # View logs
   docker-compose logs -f collector
   ```

#### Windows

1. **Manual Collection**:
   ```cmd
   # Activate your virtual environment if using local setup
   venv\Scripts\activate
   
   # Run the collector script
   python python\collectors\iracing_collector_prometheus.py
   ```

2. **Using Docker**:
   ```cmd
   # Trigger the collector container
   docker-compose restart collector
   
   # View logs
   docker-compose logs -f collector
   ```

### Viewing Dashboards

1. Open Grafana in your browser at http://localhost:3000 (or the custom port configured in your `.env` file)
2. Navigate to Dashboards > Browse
3. Select one of the available iRacing dashboards

### Customizing Dashboards

1. Open a dashboard in Grafana
2. Click the gear icon to edit
3. Customize panels as needed
4. Save your changes

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
   - Check database logs: `docker-compose logs postgres prometheus`

3. **Dashboard Not Loading Data**:
   - Verify data source configuration in Grafana
   - Check that data collection has run successfully
   - Examine Grafana logs: `docker-compose logs dashboard`

4. **Docker Compose Issues**:
   - Verify Docker and Docker Compose are installed correctly
   - Check that ports are not already in use (5432, 9090, 8000)
   - The setup script automatically checks if port 3000 is already in use and configures an alternative port in that case
   - Restart the stack: `docker-compose down && docker-compose up -d`
   
### Grafana Cloud Troubleshooting

1. **Remote Write Not Working**:
   - Check your API keys and credentials in `terraform.tfvars`
   - Verify that your local Prometheus can reach the internet
   - Check Prometheus logs: `docker-compose logs prometheus`
   
2. **Dashboards Not Showing in Grafana Cloud**:
   - Verify Terraform applied successfully
   - Check for errors in Terraform output
   - Try running `terraform apply` again

3. **API Key Issues**:
   - API keys have different roles (Admin, Editor, Viewer)
   - Make sure you're using an Admin key for Terraform
   - Editor key should be used for metrics publishing
   
4. **Data Missing in Cloud But Present Locally**:
   - Check the remote_write configuration in Prometheus
   - Verify your Grafana Cloud stack is on a paid plan if you exceed free limits
   - Check if metrics are being sent with `curl localhost:9090/api/v1/targets` to see scrape status

### Platform-Specific Troubleshooting

#### macOS Issues

1. **Performance Issues**:
   - Docker Desktop on Mac may use excessive CPU/memory. In Docker Desktop settings:
     - Limit resources in the "Resources" section
     - Enable "Use the new Virtualization framework" if available

2. **iRacing Telemetry Access**:
   - Ensure your Mac has access to the iRacing folders
   - For sim racing data, you may need to run Docker with shared folders

#### Windows Issues

1. **WSL 2 Backend**:
   - Ensure Docker Desktop is using the WSL 2 backend for better performance
   - Update WSL 2 to the latest version if you encounter issues

2. **Path Issues in Windows**:
   - Windows uses backslashes `\` while scripts may expect forward slashes `/`
   - Use Git Bash instead of CMD to avoid path issues
   - If using PowerShell, some commands may need adjustment

3. **Firewall Issues**:
   - Allow Docker through Windows Firewall
   - If running iRacing on the same machine, ensure the collector can access it

4. **Docker Volume Permissions**:
   - Windows may have permission issues with Docker volumes
   - Try running Docker Desktop as Administrator if files aren't accessible

## License

MIT

## Getting Help With Grafana Cloud

If you're new to Grafana Cloud or having issues with the setup:

1. **Grafana Cloud Documentation**:
   - Visit [Grafana Cloud Documentation](https://grafana.com/docs/grafana-cloud/) for official guides
   - Check the [Getting Started](https://grafana.com/docs/grafana-cloud/getting-started/) section

2. **Free Tier Limitations**:
   - The free tier includes 10,000 series metrics and 50GB of logs
   - Check your usage in Grafana Cloud's "Usage & Billing" section
   - For most iRacers, this should be sufficient unless you're collecting data very frequently

3. **Community Support**:
   - Join the [Grafana Community Forums](https://community.grafana.com/)
   - Post on [r/iRacing](https://www.reddit.com/r/iRacing/) if you need help with the iRacing specific integration
   
4. **Creating an Account**:
   - Visit [Grafana Cloud Signup](https://grafana.com/auth/sign-up/create-user)
   - You can use your Google/GitHub account or create a new one with email
   - No credit card required for the free tier

5. **Upgrading**:
   - If you find you need more capacity, paid tiers start at $49/month
   - Team accounts allow sharing dashboards with multiple users

## Acknowledgements

- [iRacing](https://www.iracing.com/) for their simulator and API
- [Grafana](https://grafana.com/) for the visualization platform
- [Grafana Cloud](https://grafana.com/products/cloud/) for the cloud-hosted option
- [Prometheus](https://prometheus.io/) for time-series data storage
- [PostgreSQL](https://www.postgresql.org/) for relational data storage
- [pyRacing](https://github.com/Esterni/pyracing) for Python iRacing API client
- [irsdk](https://github.com/kutu/pyirsdk) for iRacing telemetry access
