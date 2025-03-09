terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
    }
    http = {
      source = "hashicorp/http"
    }
  }
}

# Create Grafana folders
resource "grafana_folder" "performance" {
  title = "iRacing Performance"
}

resource "grafana_folder" "telemetry" {
  title = "iRacing Telemetry"
}

resource "grafana_folder" "strategy" {
  title = "iRacing Strategy"
}

resource "grafana_folder" "trends" {
  title = "iRacing Trends"
}

# Import dashboards
resource "grafana_dashboard" "lap_times" {
  folder      = grafana_folder.performance.id
  config_json = file("${path.module}/dashboards/lap_times.json")
}

resource "grafana_dashboard" "car_telemetry" {
  folder      = grafana_folder.telemetry.id
  config_json = file("${path.module}/dashboards/car_telemetry.json")
}

resource "grafana_dashboard" "race_strategy" {
  folder      = grafana_folder.strategy.id
  config_json = file("${path.module}/dashboards/race_strategy.json")
}

resource "grafana_dashboard" "performance_trends" {
  folder      = grafana_folder.trends.id
  config_json = file("${path.module}/dashboards/performance_trends.json")
}

# Define an API token - this creates a service account and token
resource "grafana_api_key" "metrics_publisher" {
  name            = "iRacing Metrics Publisher"
  role            = "Editor"
  seconds_to_live = 60 * 60 * 24 * 30 # 30 days
}

# Store key in local file for reference
resource "local_file" "metrics_api_key" {
  content  = grafana_api_key.metrics_publisher.key
  filename = "${path.module}/metrics_api_key.txt"
}

# Create a Prometheus data source for remote metrics
resource "grafana_data_source" "prometheus_remote" {
  name = "Prometheus-iRacing-Remote"
  type = "prometheus"
  url  = "https://prometheus-${var.stack_slug}.grafana.net/api/prom"
  
  json_data {
    http_method     = "GET"
    time_interval   = "15s"
  }
  
  secure_json_data {
    basic_auth_password = var.grafana_cloud_api_key
  }
}