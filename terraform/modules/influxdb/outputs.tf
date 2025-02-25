output "influxdb_url" {
  description = "The URL of the InfluxDB instance"
  value       = "http://localhost:8086"
}

output "influxdb_token_file" {
  description = "File containing the InfluxDB token"
  value       = local_file.influxdb_token.filename
}
