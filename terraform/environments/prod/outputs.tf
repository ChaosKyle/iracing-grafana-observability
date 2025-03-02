output "grafana_cloud_url" {
  description = "URL to access Grafana Cloud instance"
  value       = var.grafana_cloud_url
}

output "postgres_connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgres://${var.postgres_user}:${var.postgres_password}@${module.postgres.postgres_host}:${module.postgres.postgres_port}/${var.postgres_database}"
  sensitive   = true
}

output "prometheus_url" {
  description = "URL to access local Prometheus"
  value       = module.prometheus.prometheus_url
}

output "prometheus_remote_write_endpoint" {
  description = "Grafana Cloud Prometheus remote_write endpoint"
  value       = module.grafana_cloud.prometheus_remote_write_endpoint
}