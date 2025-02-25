resource "docker_image" "postgres" {
  name = "postgres:14"
}

resource "docker_container" "postgres" {
  name  = "iracing-postgres"
  image = docker_image.postgres.image_id
  
  ports {
    internal = 5432
    external = 5432
  }
  
  env = [
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_database}"
  ]
  
  volumes {
    container_path = "/var/lib/postgresql/data"
    host_path      = var.postgres_data_path
  }
}

# Initialize database schema
resource "null_resource" "postgres_schema" {
  depends_on = [docker_container.postgres]

  provisioner "local-exec" {
    command = "sleep 10 && psql -h localhost -U ${var.postgres_user} -d ${var.postgres_database} -f ${path.module}/schema.sql"
    environment = {
      PGPASSWORD = var.postgres_password
    }
  }
}
