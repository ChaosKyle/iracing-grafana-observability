#!/bin/bash
# Repository Setup for iRacing Grafana Project

# Create project directory
mkdir -p iracing-grafana-observability
cd iracing-grafana-observability

# Initialize git repository
git init

# Create directory structure
mkdir -p terraform/modules/{grafana,influxdb,postgres}
mkdir -p terraform/environments/{dev,prod}
mkdir -p python/{collectors,processors,utils}
mkdir -p dashboards/{performance,telemetry,strategy,trends}
mkdir -p .github/workflows
mkdir -p docs/{blog,architecture}
mkdir -p docker

# Create basic README
cat > README.md << 'EOF'
# iRacing Grafana Observability Project

A comprehensive solution for visualizing iRacing telemetry and performance data using Grafana, managed with Terraform and automated with GitHub Actions.

## Project Structure
- `/terraform` - Infrastructure as Code for Grafana, InfluxDB, and other resources
- `/python` - Data extraction and processing scripts
- `/dashboards` - Grafana dashboard definitions
- `/docs` - Blog posts and documentation
- `/docker` - Docker configurations for local development

## Getting Started
1. Clone this repository
2. Set up environment variables for iRacing API access
3. Run `./setup.sh` to initialize local environment
4. Follow instructions in the docs folder for detailed setup

## Features
- Historical iRacing data visualization
- Live telemetry streaming
- Performance metrics and trend analysis
- Race strategy insights

## License
MIT
EOF

# Create .gitignore file
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Terraform
.terraform/
terraform.tfstate
terraform.tfstate.backup
*.tfvars
.terraform.lock.hcl

# Environment variables
.env
.env.local
*.env

# Docker
*.dockerignore

# OS specific
.DS_Store
Thumbs.db

# IDEs and editors
.idea/
.vscode/
*.swp
*.swo

# Logs
logs/
*.log

# Credentials
credentials.json
*_credentials.*
EOF

# Create setup script
cat > setup.sh << 'EOF'
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
EOF

# Make setup script executable
chmod +x setup.sh

# Create requirements.txt for Python
cat > python/requirements.txt << 'EOF'
requests>=2.28.1
pandas>=1.5.0
numpy>=1.23.3
influxdb-client>=1.33.0
psycopg2-binary>=2.9.3
python-dotenv>=0.21.0
pyyaml>=6.0
pyracing>=0.1.5
matplotlib>=3.6.0
pytest>=7.0.0
black>=22.8.0
flake8>=5.0.4
EOF

echo "Repository structure created successfully!"
