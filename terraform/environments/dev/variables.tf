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

variable "influxdb_admin_user" {
  description = "InfluxDB admin username"
  default     = "admin"
}

variable "influxdb_admin_password" {
  description = "InfluxDB admin password"
  sensitive   = true
}

variable "influxdb_org" {
  description = "InfluxDB organization name"
  default     = "iracing"
}

variable "influxdb_bucket" {
  description = "InfluxDB bucket name"
  default     = "iracing_telemetry"
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
