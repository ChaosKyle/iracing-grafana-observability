variable "grafana_cloud_url" {
  description = "The URL of the Grafana Cloud instance"
  type        = string
}

variable "grafana_cloud_api_key" {
  description = "The API key for Grafana Cloud"
  type        = string
  sensitive   = true
}

variable "grafana_cloud_org_id" {
  description = "The organization ID for Grafana Cloud"
  type        = string
}

variable "stack_slug" {
  description = "The Grafana Cloud stack slug"
  type        = string
}

variable "grafana_admin_user" {
  description = "Grafana admin username"
  default     = "admin"
}

variable "grafana_admin_pass" {
  description = "Grafana admin password"
  sensitive   = true
}

variable "docker_host" {
  description = "Docker host address"
  default     = "unix:///var/run/docker.sock"
}

variable "prometheus_data_path" {
  description = "Path to store Prometheus data"
  default     = "/var/lib/prometheus"
}

variable "prometheus_port" {
  description = "External port for Prometheus"
  default     = 9090
}

variable "grafana_metrics_publisher_id" {
  description = "Grafana Cloud metrics publisher ID (username for remote_write)"
  type        = string
}

variable "grafana_metrics_api_key" {
  description = "Grafana Cloud metrics API key (password for remote_write)"
  type        = string
  sensitive   = true
}

variable "postgres_user" {
  description = "PostgreSQL username"
  default     = "postgres"
}

variable "postgres_password" {
  description = "PostgreSQL password"
  sensitive   = true
}

variable "postgres_database" {
  description = "PostgreSQL database name"
  default     = "iracing_data"
}