output "prometheus_remote_write_endpoint" {
  description = "Prometheus remote_write endpoint URL for Grafana Cloud"
  value       = "https://prometheus-${var.stack_slug}.grafana.net/api/prom/push"
}

output "metrics_publisher_id" {
  description = "The ID of the service account created for metrics publishing"
  value       = grafana_api_key.metrics_publisher.id
}

output "metrics_api_key" {
  description = "The API key for the metrics publisher"
  value       = grafana_api_key.metrics_publisher.key
  sensitive   = true
}