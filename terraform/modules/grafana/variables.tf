variable "grafana_url" {
  description = "The URL of the Grafana instance"
  type        = string
}

variable "grafana_admin_user" {
  description = "Grafana admin username"
  type        = string
}

variable "grafana_admin_pass" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
}

variable "influxdb_url" {
  description = "InfluxDB URL"
  type        = string
}

variable "influxdb_token" {
  description = "InfluxDB access token"
  type        = string
  sensitive   = true
  default     = ""
}

variable "postgres_host" {
  description = "PostgreSQL host"
  type        = string
}

variable "postgres_port" {
  description = "PostgreSQL port"
  type        = number
  default     = 5432
}

variable "postgres_user" {
  description = "PostgreSQL username"
  type        = string
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "postgres_database" {
  description = "PostgreSQL database name"
  type        = string
}
