variable "prometheus_data_path" {
  description = "Path to the Prometheus data directory on the host"
  default     = "/var/lib/prometheus"
}

variable "prometheus_port" {
  description = "External port for Prometheus"
  default     = 9090
}

variable "remote_write_enabled" {
  description = "Enable remote_write to Grafana Cloud"
  type        = bool
  default     = false
}

variable "remote_write_url" {
  description = "URL for Prometheus remote_write"
  type        = string
  default     = ""
}

variable "remote_write_username" {
  description = "Username for Prometheus remote_write"
  type        = string
  default     = ""
}

variable "remote_write_password" {
  description = "Password for Prometheus remote_write"
  type        = string
  sensitive   = true
  default     = ""
}