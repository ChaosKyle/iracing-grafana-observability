#!/bin/bash
# Setup script for local development environment

echo "Setting up iRacing Grafana Observability Project..."

# Check for required tools
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "Terraform is required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }

# Create virtual environment for Python if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r python/requirements.txt
else
    echo "Python virtual environment already exists. Activating..."
    source venv/bin/activate
fi

# Check if environment file exists
if [ ! -f ".env" ]; then
    echo "Creating sample .env file from template..."
    cp docker/collector/config.env .env
    echo "Please edit .env file with your credentials before continuing."
fi

# Create Docker volumes if they don't exist
docker volume ls | grep -q "iracing-grafana-observability_postgres-data" || docker volume create iracing-grafana-observability_postgres-data
docker volume ls | grep -q "iracing-grafana-observability_influxdb-data" || docker volume create iracing-grafana-observability_influxdb-data

# Initialize Terraform
echo "Initializing Terraform..."
cd terraform/environments/dev
terraform init

# Give instructions for next steps
echo
echo "Setup complete! Next steps:"
echo
echo "1. Edit .env file with your iRacing credentials and database passwords"
echo "2. Start the stack with: docker-compose up -d"
echo "3. Access Grafana at: http://localhost:3000 (default login: admin/admin)"
echo "4. To run the collector manually: python python/collectors/iracing_collector.py"
echo
echo "For cloud deployment with Terraform:"
echo "1. cd terraform/environments/dev"
echo "2. cp terraform.tfvars.example terraform.tfvars"
echo "3. Edit terraform.tfvars with your credentials"
echo "4. terraform apply"
echo
echo "For more information, see the documentation in docs/ directory."