#!/bin/bash
# Setup script for local development environment

echo "Setting up iRacing Grafana Observability Project..."

# Check for required tools
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v kind >/dev/null 2>&1 || { echo "Kind is required but not installed. Aborting." >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "Terraform is required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }

# Create virtual environment for Python
python3 -m venv venv
source venv/bin/activate
pip install -r python/requirements.txt

# Create Kind cluster if it doesn't exist
if ! kind get clusters | grep -q "iracing-grafana"; then
    echo "Creating Kind cluster..."
    kind create cluster --name iracing-grafana
fi

# Initialize Terraform
cd terraform/environments/dev
terraform init

echo "Setup complete! You can now run the following commands:"
echo "1. source venv/bin/activate"
echo "2. cd terraform/environments/dev"
echo "3. terraform apply"
echo "4. python python/collectors/iracing_collector.py"
