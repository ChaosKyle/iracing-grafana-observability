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
