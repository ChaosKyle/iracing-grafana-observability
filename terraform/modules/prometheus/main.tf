terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

resource "docker_image" "prometheus" {
  name = "prom/prometheus:latest"
}

resource "docker_container" "prometheus" {
  name  = "iracing-prometheus"
  image = docker_image.prometheus.image_id
  
  ports {
    internal = 9090
    external = 9090
  }
  
  volumes {
    container_path = "/etc/prometheus/prometheus.yml"
    host_path      = "${path.module}/prometheus.yml"
  }
  
  volumes {
    container_path = "/prometheus"
    host_path      = var.prometheus_data_path
  }
}

# Copy prometheus.yml config file to module directory
resource "local_file" "prometheus_config" {
  filename = "${path.module}/prometheus.yml"
  content  = var.remote_write_enabled ? local.prometheus_config_with_remote_write : local.prometheus_config_basic
}

locals {
  prometheus_config_basic = <<-EOT
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'iracing_collector'
    static_configs:
      - targets: ['collector:8000']

  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
EOT

  prometheus_config_with_remote_write = <<-EOT
global:
  scrape_interval: 15s
  evaluation_interval: 15s

remote_write:
  - url: ${var.remote_write_url}
    basic_auth:
      username: ${var.remote_write_username}
      password: ${var.remote_write_password}

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'iracing_collector'
    static_configs:
      - targets: ['collector:8000']

  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
EOT
}