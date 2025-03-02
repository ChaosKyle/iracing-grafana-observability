variable "prometheus_data_path" {
  description = "Path to the Prometheus data directory on the host"
  default     = "/var/lib/prometheus"
}

variable "prometheus_port" {
  description = "External port for Prometheus"
  default     = 9090
}