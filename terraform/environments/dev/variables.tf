variable "grafana_url" {
  description = "The URL of the Grafana instance"
  default     = "http://localhost:3000"
}

variable "grafana_auth" {
  description = "The API key or basic auth for Grafana API"
  sensitive   = true
}

variable "grafana_admin_user" {
  description = "Grafana admin username"
  default     = "admin"
}

variable "grafana_admin_pass" {
  description = "Grafana admin password"
  sensitive   = true
  default     = "admin"
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
