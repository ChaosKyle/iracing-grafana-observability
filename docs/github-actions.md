# GitHub Actions Workflows

This document describes the GitHub Actions workflows used in the iRacing Grafana Observability project.

## Overview

GitHub Actions automate our continuous integration and delivery processes, ensuring code quality and facilitating deployment. Our workflows handle:

- Python code testing and linting
- Docker image building and publishing
- Dashboard validation
- Automated data collection

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

### 2. Docker Build & Push (`docker-build.yml`)

This workflow builds and publishes Docker images to GitHub Container Registry:

- **Triggers**: Push or pull request to main/master that changes Docker files
- **Actions**:
  - Sets up Docker Buildx
  - Logs in to GitHub Container Registry
  - Builds and tags collector image
  - Builds and tags dashboard image
  - Pushes images to GHCR when on main/master branch

Example variable configuration:
```yaml
REGISTRY: 'ghcr.io'
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

### 4. Data Collection (`data-collection.yml`)

This workflow automatically collects data from iRacing:

- **Triggers**: Schedule (every 6 hours) or manual trigger
- **Actions**:
  - Sets up Python environment
  - Runs data collection script
  - Uploads logs as artifacts

Example variable configuration:
```yaml
COLLECTOR_SCRIPT: 'python/collectors/iracing_collector.py'
LOGS_FILE: 'iracing_collector.log'
DATA_COLLECTION_CRON: '0 */6 * * *'
```

### 5. Reusable Actions (`reusable-actions.yml`)

This workflow contains reusable job definitions for other workflows:

- **Triggers**: Called by other workflows
- **Actions**:
  - Python setup action
  - Dependency installation
  - Caching for faster builds

## Required Secrets

The following secrets must be configured in your GitHub repository settings:

1. **For Docker image publishing**:
   - `GITHUB_TOKEN` (automatically provided)

2. **For data collection**:
   - `IRACING_USERNAME`
   - `IRACING_PASSWORD`
   - `POSTGRES_HOST`
   - `POSTGRES_PORT`
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB`
   - `INFLUXDB_URL`
   - `INFLUXDB_TOKEN`
   - `INFLUXDB_ORG`
   - `INFLUXDB_BUCKET`

## Setting Up Repository Secrets

1. Navigate to your GitHub repository
2. Go to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Add each required secret with its appropriate value

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

4. **Data collection failures**:
   - Check secret values are correctly configured
   - Verify network access to external services

## Workflow Logs and Artifacts

Workflow run logs and artifacts are available in the GitHub Actions UI:

1. Go to the Actions tab in your repository
2. Select the workflow run you want to inspect
3. Download artifacts or view logs for specific steps