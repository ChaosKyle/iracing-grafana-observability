resource "docker_image" "influxdb" {
  name = "influxdb:2.6"
}

resource "docker_container" "influxdb" {
  name  = "iracing-influxdb"
  image = docker_image.influxdb.image_id
  
  ports {
    internal = 8086
    external = 8086
  }
  
  env = [
    "DOCKER_INFLUXDB_INIT_MODE=setup",
    "DOCKER_INFLUXDB_INIT_USERNAME=${var.influxdb_admin_user}",
    "DOCKER_INFLUXDB_INIT_PASSWORD=${var.influxdb_admin_password}",
    "DOCKER_INFLUXDB_INIT_ORG=${var.influxdb_org}",
    "DOCKER_INFLUXDB_INIT_BUCKET=${var.influxdb_bucket}"
  ]
  
  volumes {
    container_path = "/var/lib/influxdb2"
    host_path      = var.influxdb_data_path
  }
}

# Output variable to store InfluxDB token
resource "local_file" "influxdb_token" {
  filename = "${path.module}/influxdb_token.txt"
  content  = "Replace this with your InfluxDB token after setup"
}
