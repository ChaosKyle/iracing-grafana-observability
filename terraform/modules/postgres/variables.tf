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

variable "postgres_data_path" {
  description = "Path to store PostgreSQL data"
  type        = string
  default     = "./postgres-data"
}
