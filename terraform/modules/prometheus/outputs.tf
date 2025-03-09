output "prometheus_url" {
  description = "URL to access Prometheus"
  value       = "http://localhost:${var.prometheus_port}"
}

output "prometheus_host" {
  description = "Docker container hostname for Prometheus"
  value       = docker_container.prometheus.name
}

output "prometheus_port" {
  description = "Prometheus port"
  value       = var.prometheus_port
}