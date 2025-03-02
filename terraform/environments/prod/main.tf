terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "~> 1.36.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
    local = {
      source  = "hashicorp/local"
    }
  }
  
  backend "local" {
    path = "terraform.tfstate"
  }
}

# Grafana Cloud Provider
provider "grafana" {
  url  = var.grafana_cloud_url
  auth = var.grafana_cloud_api_key
}

# Docker provider for local Prometheus and PostgreSQL
provider "docker" {
  host = var.docker_host
}

# Grafana Cloud Module
module "grafana_cloud" {
  source = "../../modules/grafana_cloud"
  
  stack_slug              = var.stack_slug
  grafana_cloud_api_key   = var.grafana_cloud_api_key
  grafana_cloud_org_id    = var.grafana_cloud_org_id
  grafana_admin_user      = var.grafana_admin_user
  grafana_admin_pass      = var.grafana_admin_pass
}

# Prometheus for local metrics collection
module "prometheus" {
  source = "../../modules/prometheus"
  
  prometheus_data_path = var.prometheus_data_path
  prometheus_port      = var.prometheus_port
  
  # Add remote_write configuration for Grafana Cloud
  remote_write_enabled = true
  remote_write_url     = module.grafana_cloud.prometheus_remote_write_endpoint
  remote_write_username = var.grafana_metrics_publisher_id
  remote_write_password = var.grafana_metrics_api_key
}

# PostgreSQL for local data storage
module "postgres" {
  source = "../../modules/postgres"
  
  postgres_user       = var.postgres_user
  postgres_password   = var.postgres_password
  postgres_database   = var.postgres_database
}