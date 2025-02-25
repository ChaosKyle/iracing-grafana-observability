output "postgres_host" {
  description = "PostgreSQL host"
  value       = "localhost"
}

output "postgres_port" {
  description = "PostgreSQL port"
  value       = 5432
}

output "connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgres://${var.postgres_user}:${var.postgres_password}@localhost:5432/${var.postgres_database}"
  sensitive   = true
}
