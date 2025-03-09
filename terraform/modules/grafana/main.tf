terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
    }
  }
}

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

# Prometheus Data Source
resource "grafana_data_source" "prometheus" {
  type       = "prometheus"
  name       = "Prometheus-iRacing"
  url        = var.prometheus_url
  is_default = true
  
  json_data {
    http_method     = "GET"
    time_interval   = "15s"
  }
}

# PostgreSQL Data Source
resource "grafana_data_source" "postgres" {
  type       = "postgres"
  name       = "PostgreSQL-iRacing"
  url        = "${var.postgres_host}:${var.postgres_port}"
  database   = var.postgres_database
  username   = var.postgres_user
  
  secure_json_data {
    password = var.postgres_password
  }
  
  json_data {
    ssl_mode       = "disable"
    max_idle_conns = 10
    max_open_conns = 100
    timeout        = 30
  }
}

# Example dashboard for lap times
resource "grafana_dashboard" "lap_times" {
  folder      = grafana_folder.performance.id
  config_json = file("${path.module}/dashboards/lap_times.json")
}

# Example dashboard for car telemetry
resource "grafana_dashboard" "car_telemetry" {
  folder      = grafana_folder.telemetry.id
  config_json = file("${path.module}/dashboards/car_telemetry.json")
}

# Example dashboard for race strategy
resource "grafana_dashboard" "race_strategy" {
  folder      = grafana_folder.strategy.id
  config_json = file("${path.module}/dashboards/race_strategy.json")
}

# Example dashboard for performance trends
resource "grafana_dashboard" "performance_trends" {
  folder      = grafana_folder.trends.id
  config_json = file("${path.module}/dashboards/performance_trends.json")
}
