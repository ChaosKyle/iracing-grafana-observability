variable "stack_slug" {
  description = "The Grafana Cloud stack slug"
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

variable "grafana_admin_user" {
  description = "Grafana admin username"
  type        = string
}

variable "grafana_admin_pass" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
}