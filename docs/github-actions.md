# GitHub Actions Workflows

This document describes the GitHub Actions workflows used in the iRacing Grafana Observability project for development purposes.

## Overview

GitHub Actions automate our testing and validation processes, ensuring code quality during development. Our workflows handle:

- Python code testing and linting
- Docker image building verification
- Dashboard validation
- Automated testing

## Workflow Configuration

Workflow configurations are centralized in `.github/variables.yaml` to make maintenance easier. To modify workflow behavior, update the variables in this file rather than editing individual workflow files.

## Available Workflows

### 1. Python CI (`python-ci.yml`)

This workflow validates Python code changes:

- **Triggers**: Push or pull request to main/master that changes Python files
- **Actions**:
  - Sets up Python environment
  - Installs dependencies
  - Runs linting (flake8)
  - Executes tests (pytest)

Example variable configuration:
```yaml
PYTHON_VERSION: '3.10'
PYTHON_PATH: 'python'
MAX_LINE_LENGTH: 127
MAX_COMPLEXITY: 10
```

### 2. Docker Build (`docker-build.yml`)

This workflow validates Docker configurations:

- **Triggers**: Push or pull request to main/master that changes Docker files
- **Actions**:
  - Sets up Docker Buildx
  - Builds collector image for testing
  - Builds dashboard image for testing

Example variable configuration:
```yaml
COLLECTOR_IMAGE_NAME: 'iracing-collector'
DASHBOARD_IMAGE_NAME: 'iracing-dashboard'
DOCKER_PATH: 'docker'
```

### 3. Dashboard Validator (`dashboard-validator.yml`)

This workflow validates Grafana dashboard JSON files:

- **Triggers**: Push or pull request to main/master that changes dashboard files
- **Actions**:
  - Sets up Python environment
  - Runs dashboard validator script
  - Checks for unique dashboard IDs

Example variable configuration:
```yaml
DASHBOARDS_PATH: 'terraform/modules/grafana/dashboards'
```

### 4. Reusable Actions (`reusable-actions.yml`)

This workflow contains reusable job definitions for other workflows:

- **Triggers**: Called by other workflows
- **Actions**:
  - Python setup action
  - Dependency installation
  - Caching for faster builds

## Setting Up Local Testing

Instead of relying solely on GitHub Actions, you can run the same validation checks locally:

### Running Python Tests

```bash
# Install test dependencies
pip install pytest flake8

# Run linting
flake8 python/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Run tests
pytest python/tests/
```

### Validating Dashboards

```bash
# Install validation dependencies
pip install jsonschema pyyaml

# Validate dashboard JSON files
python python/utils/dashboard_validator.py terraform/modules/grafana/dashboards/

# Check for unique dashboard IDs
python python/utils/check_dashboard_ids.py terraform/modules/grafana/dashboards/
```

### Testing Docker Builds

```bash
# Build collector image
docker build -t iracing-collector -f docker/collector/Dockerfile .

# Build dashboard image
docker build -t iracing-dashboard -f docker/dashboard/Dockerfile .
```

## Workflow Customization

To modify workflow behavior:

1. Edit `.github/variables.yaml` to update global settings
2. For more significant changes, edit the workflow files directly in `.github/workflows/`

## Workflow Triggers

You can manually trigger workflows that support the `workflow_dispatch` event:

1. Go to the Actions tab in your GitHub repository
2. Select the workflow you want to run
3. Click "Run workflow"

## Troubleshooting

### Common Issues

1. **Workflows not running**:
   - Check the workflow file path pattern matches your changes
   - Ensure branch name matches trigger configuration

2. **Docker build failures**:
   - Verify Dockerfile syntax
   - Check that required files are available in the build context

3. **Dashboard validation failures**:
   - Ensure dashboard JSON is valid
   - Check for duplicate dashboard IDs
   - Verify required fields are present

4. **Test failures**:
   - Run tests locally to debug: `pytest python/tests/`
   - Check requirements are installed: `pip install -r python/requirements.txt`

## Workflow Logs

Workflow run logs are available in the GitHub Actions UI:

1. Go to the Actions tab in your repository
2. Select the workflow run you want to inspect
3. View logs for specific steps