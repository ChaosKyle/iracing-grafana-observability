variable "influxdb_admin_user" {
  description = "InfluxDB admin username"
  type        = string
}

variable "influxdb_admin_password" {
  description = "InfluxDB admin password"
  type        = string
  sensitive   = true
}

variable "influxdb_org" {
  description = "InfluxDB organization name"
  type        = string
}

variable "influxdb_bucket" {
  description = "InfluxDB bucket name"
  type        = string
}

variable "influxdb_data_path" {
  description = "Path to store InfluxDB data"
  type        = string
  default     = "./influxdb-data"
}
