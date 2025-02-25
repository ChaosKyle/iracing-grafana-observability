output "grafana_url" {
  description = "The URL of the Grafana instance"
  value       = module.grafana.grafana_url
}

output "influxdb_url" {
  description = "The URL of the InfluxDB instance"
  value       = module.influxdb.influxdb_url
}

output "postgres_connection_string" {
  description = "PostgreSQL connection string"
  value       = module.postgres.connection_string
  sensitive   = true
}
