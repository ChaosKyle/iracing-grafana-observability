# CI/CD Workflows for iRacing Grafana Observability

This document outlines the CI/CD workflows for the iRacing Grafana Observability project and how they work together to ensure code quality and reliable deployments.

## Overall CI/CD Architecture

```
                    ┌─────────────────┐
                    │   Code Commit   │
                    └────────┬────────┘
                             │
               ┌─────────────┴─────────────┐
               │                           │
    ┌──────────▼─────────┐     ┌──────────▼─────────┐
    │  Quality Checks    │     │ Build & Test       │
    │  - Python CI       │     │ - Docker Build     │
    │  - Dashboard Valid │     │ - Security Scan    │
    └──────────┬─────────┘     └──────────┬─────────┘
               │                           │
               └─────────────┬─────────────┘
                             │
                    ┌────────▼────────┐
                    │   Terraform     │
                    │   Validation    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Auto-deploy    │
                    │  to Dev Env     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Manual deploy  │
                    │  to Prod Env    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     Tag     │
                    │     Creation    │
                    └─────────────────┘
```

## Workflow Overview

| Workflow File | Purpose | Trigger |
|---------------|---------|---------|
| `python-ci.yml` | Run tests, linting, and code coverage for Python code | Python code changes |
| `dashboard-validator.yml` | Validate Grafana dashboard JSON definitions | Dashboard changes |
| `docker-build.yml` | Build Docker images and run security scans | Docker or Python changes |
| `terraform.yaml` | Validate and apply Terraform configuration | Terraform changes |
| `release.yml` | Create GitHub Releases and publish Docker images | Git tags or manual |

## Github Environments

The project uses GitHub Environments for managing different deployment targets:

- `dev` - Development environment (auto-deployed)
- `prod` - Production environment using Grafana Cloud (manual deployment)

## Key Workflow Details

### Python CI

Performs code quality checks on Python code:

- Executes unit tests with pytest
- Runs linting with flake8
- Measures test coverage with pytest-cov
- Uploads coverage reports to Codecov

### Docker Build

Builds and tests Docker images:

- Uses buildx for efficient builds
- Publishes images to GitHub Container Registry
- Tags images with SHA and branch/PR references
- Runs Trivy security scanning for vulnerabilities

### Dashboard Validator

Ensures Grafana dashboards are valid:

- Validates dashboard JSON structure
- Checks for unique dashboard IDs
- Compares local and cloud dashboard configurations
- Ensures consistency across environments

### Terraform CI/CD

Manages infrastructure as code:

- Validates Terraform configurations
- Auto-applies changes to dev environment
- Requires manual approval for prod environment
- Supports both local Grafana and Grafana Cloud

### Release Workflow

Automates release process:

- Triggered by version tags or manually
- Builds and publishes versioned Docker images
- Generates changelogs from commits
- Creates GitHub releases

## Recommended Workflow for Feature Development

1. Create a feature branch
2. Develop and test locally
3. Open a pull request
4. CI workflows run automatically
5. Review and approve PR
6. Merge to master
7. Auto-deploy to dev environment
8. Test in dev
9. Manually deploy to prod using workflow dispatch
10. Create a release using the release workflow

## Environment Variables and Secrets

The following secrets are required:

- `GRAFANA_AUTH` - Grafana API key for dev environment
- `GRAFANA_ADMIN_PASS` - Grafana admin password
- `POSTGRES_PASSWORD` - PostgreSQL password
- `GRAFANA_CLOUD_API_KEY` - Grafana Cloud API key
- `GRAFANA_CLOUD_ORG_ID` - Grafana Cloud organization ID
- `GRAFANA_METRICS_API_KEY` - API key for metrics publishing
- `GRAFANA_METRICS_PUBLISHER_ID` - Publisher ID for metrics

## Setting Up GitHub Secrets

1. Go to repository Settings
2. Navigate to Secrets > Actions
3. Add repository secrets
4. Set up environment secrets for dev and prod environments
