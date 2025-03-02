# Grafana Cloud Dashboards

This directory contains dashboards for the Grafana Cloud instance. The dashboards will be automatically deployed to Grafana Cloud when the Terraform module is applied.

Dashboard files are symlinked from the `modules/grafana/dashboards` directory to maintain a single source of truth.

## Creating Symlinks

To create the symlinks:

```bash
cd terraform/modules/grafana_cloud/dashboards
ln -s ../../grafana/dashboards/*.json .
```

This will link all the JSON dashboard files from the local Grafana module to this directory.