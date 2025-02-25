#!/bin/bash
# Terraform Scaffolding Script for iRacing Grafana Project

echo "Creating Terraform scaffold for iRacing Grafana Project..."

# Create main Terraform configuration files for dev environment
mkdir -p terraform/environments/dev
cat > terraform/environments/dev/main.tf << 'EOF'
terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "~> 1.36.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.16.0"
    }
  }
  
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "grafana" {
  url  = var.grafana_url
  auth = var.grafana_auth
}

provider "docker" {
  host = var.docker_host
}

provider "kubernetes" {
  config_path = "~/.kube/config"
  config_context = "kind-iracing-grafana"
}

module "grafana" {
  source = "../../modules/grafana"
  
  grafana_url         = var.grafana_url
  grafana_admin_user  = var.grafana_admin_user
  grafana_admin_pass  = var.grafana_admin_pass
  influxdb_url        = module.influxdb.influxdb_url
  postgres_host       = module.postgres.postgres_host
  postgres_port       = module.postgres.postgres_port
  postgres_user       = var.postgres_user
  postgres_password   = var.postgres_password
  postgres_database   = var.postgres_database
}

module "influxdb" {
  source = "../../modules/influxdb"
  
  influxdb_admin_user     = var.influxdb_admin_user
  influxdb_admin_password = var.influxdb_admin_password
  influxdb_org            = var.influxdb_org
  influxdb_bucket         = var.influxdb_bucket
}

module "postgres" {
  source = "../../modules/postgres"
  
  postgres_user       = var.postgres_user
  postgres_password   = var.postgres_password
  postgres_database   = var.postgres_database
}
EOF

# Create variables file for dev environment
cat > terraform/environments/dev/variables.tf << 'EOF'
variable "grafana_url" {
  description = "The URL of the Grafana instance"
  default     = "http://localhost:3000"
}

variable "grafana_auth" {
  description = "The API key or basic auth for Grafana API"
  sensitive   = true
}

variable "grafana_admin_user" {
  description = "Grafana admin username"
  default     = "admin"
}

variable "grafana_admin_pass" {
  description = "Grafana admin password"
  sensitive   = true
  default     = "admin"
}

variable "docker_host" {
  description = "Docker host address"
  default     = "unix:///var/run/docker.sock"
}

variable "influxdb_admin_user" {
  description = "InfluxDB admin username"
  default     = "admin"
}

variable "influxdb_admin_password" {
  description = "InfluxDB admin password"
  sensitive   = true
}

variable "influxdb_org" {
  description = "InfluxDB organization name"
  default     = "iracing"
}

variable "influxdb_bucket" {
  description = "InfluxDB bucket name"
  default     = "iracing_telemetry"
}

variable "postgres_user" {
  description = "PostgreSQL username"
  default     = "postgres"
}

variable "postgres_password" {
  description = "PostgreSQL password"
  sensitive   = true
}

variable "postgres_database" {
  description = "PostgreSQL database name"
  default     = "iracing_data"
}
EOF

# Create outputs file for dev environment
cat > terraform/environments/dev/outputs.tf << 'EOF'
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
EOF

# Create terraform.tfvars.example file for dev environment
cat > terraform/environments/dev/terraform.tfvars.example << 'EOF'
grafana_url           = "http://localhost:3000"
grafana_auth          = "admin:admin"
grafana_admin_user    = "admin"
grafana_admin_pass    = "securepassword"

docker_host           = "unix:///var/run/docker.sock"

influxdb_admin_user     = "admin"
influxdb_admin_password = "influxdb_password"
influxdb_org            = "iracing"
influxdb_bucket         = "iracing_telemetry"

postgres_user         = "postgres"
postgres_password     = "postgres_password"
postgres_database     = "iracing_data"
EOF

# Create Grafana module
mkdir -p terraform/modules/grafana
cat > terraform/modules/grafana/main.tf << 'EOF'
resource "grafana_folder" "performance" {
  title = "iRacing Performance"
}

resource "grafana_folder" "telemetry" {
  title = "iRacing Telemetry"
}

resource "grafana_folder" "strategy" {
  title = "iRacing Strategy"
}

resource "grafana_folder" "trends" {
  title = "iRacing Trends"
}

# InfluxDB Data Source
resource "grafana_data_source" "influxdb" {
  type       = "influxdb"
  name       = "InfluxDB-iRacing"
  url        = var.influxdb_url
  is_default = true
  
  json_data {
    default_bucket = "iracing_telemetry"
    organization   = "iracing"
    version        = "Flux"
  }
  
  secure_json_data {
    token = var.influxdb_token
  }
}

# PostgreSQL Data Source
resource "grafana_data_source" "postgres" {
  type       = "postgres"
  name       = "PostgreSQL-iRacing"
  url        = "${var.postgres_host}:${var.postgres_port}"
  database   = var.postgres_database
  username   = var.postgres_user
  
  secure_json_data {
    password = var.postgres_password
  }
  
  json_data {
    ssl_mode       = "disable"
    max_idle_conns = 10
    max_open_conns = 100
    timeout        = 30
  }
}

# Example dashboard for lap times
resource "grafana_dashboard" "lap_times" {
  folder      = grafana_folder.performance.id
  config_json = file("${path.module}/dashboards/lap_times.json")
}

# Example dashboard for car telemetry
resource "grafana_dashboard" "car_telemetry" {
  folder      = grafana_folder.telemetry.id
  config_json = file("${path.module}/dashboards/car_telemetry.json")
}

# Example dashboard for race strategy
resource "grafana_dashboard" "race_strategy" {
  folder      = grafana_folder.strategy.id
  config_json = file("${path.module}/dashboards/race_strategy.json")
}

# Example dashboard for performance trends
resource "grafana_dashboard" "performance_trends" {
  folder      = grafana_folder.trends.id
  config_json = file("${path.module}/dashboards/performance_trends.json")
}
EOF

# Create variables file for Grafana module
cat > terraform/modules/grafana/variables.tf << 'EOF'
variable "grafana_url" {
  description = "The URL of the Grafana instance"
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

variable "influxdb_url" {
  description = "InfluxDB URL"
  type        = string
}

variable "influxdb_token" {
  description = "InfluxDB access token"
  type        = string
  sensitive   = true
  default     = ""
}

variable "postgres_host" {
  description = "PostgreSQL host"
  type        = string
}

variable "postgres_port" {
  description = "PostgreSQL port"
  type        = number
  default     = 5432
}

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
EOF

# Create outputs file for Grafana module
cat > terraform/modules/grafana/outputs.tf << 'EOF'
output "grafana_url" {
  description = "The URL of the Grafana instance"
  value       = var.grafana_url
}

output "dashboard_urls" {
  description = "URLs for all created dashboards"
  value = {
    lap_times         = "${var.grafana_url}/d/${grafana_dashboard.lap_times.dashboard_id}"
    car_telemetry     = "${var.grafana_url}/d/${grafana_dashboard.car_telemetry.dashboard_id}"
    race_strategy     = "${var.grafana_url}/d/${grafana_dashboard.race_strategy.dashboard_id}"
    performance_trends = "${var.grafana_url}/d/${grafana_dashboard.performance_trends.dashboard_id}"
  }
}
EOF

# Create empty dashboard JSON files
mkdir -p terraform/modules/grafana/dashboards
for dashboard in lap_times car_telemetry race_strategy performance_trends; do
  cat > terraform/modules/grafana/dashboards/${dashboard}.json << 'EOF'
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [],
  "schemaVersion": 27,
  "style": "dark",
  "tags": ["iracing", "auto-generated"],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "iRacing Dashboard - PLACEHOLDER",
  "uid": null,
  "version": 0
}
EOF
done

# Create InfluxDB module
mkdir -p terraform/modules/influxdb
cat > terraform/modules/influxdb/main.tf << 'EOF'
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
EOF

# Create variables file for InfluxDB module
cat > terraform/modules/influxdb/variables.tf << 'EOF'
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
EOF

# Create outputs file for InfluxDB module
cat > terraform/modules/influxdb/outputs.tf << 'EOF'
output "influxdb_url" {
  description = "The URL of the InfluxDB instance"
  value       = "http://localhost:8086"
}

output "influxdb_token_file" {
  description = "File containing the InfluxDB token"
  value       = local_file.influxdb_token.filename
}
EOF

# Create PostgreSQL module
mkdir -p terraform/modules/postgres
cat > terraform/modules/postgres/main.tf << 'EOF'
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
EOF

# Create schema file for PostgreSQL module
cat > terraform/modules/postgres/schema.sql << 'EOF'
-- iRacing database schema

-- Tracks table
CREATE TABLE IF NOT EXISTS tracks (
    id SERIAL PRIMARY KEY,
    iracing_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    config VARCHAR(255),
    length_km DECIMAL(10, 3),
    corners INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cars table
CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    iracing_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    class VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Driver profile table
CREATE TABLE IF NOT EXISTS driver_profile (
    id SERIAL PRIMARY KEY,
    iracing_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    irating INTEGER,
    license_class VARCHAR(10),
    license_level DECIMAL(3,2),
    safety_rating DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    iracing_session_id BIGINT UNIQUE NOT NULL,
    session_type VARCHAR(50) NOT NULL, -- Race, Practice, Qualify, etc.
    track_id INTEGER REFERENCES tracks(id),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    weather_type VARCHAR(50),
    temp_track DECIMAL(5,2),
    temp_air DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Laps table
CREATE TABLE IF NOT EXISTS laps (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    driver_id INTEGER REFERENCES driver_profile(id),
    car_id INTEGER REFERENCES cars(id),
    lap_number INTEGER NOT NULL,
    lap_time DECIMAL(10, 3), -- in seconds
    sector1_time DECIMAL(10, 3),
    sector2_time DECIMAL(10, 3),
    sector3_time DECIMAL(10, 3),
    fuel_used DECIMAL(10, 3),
    incidents INTEGER DEFAULT 0,
    valid_lap BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Race results table
CREATE TABLE IF NOT EXISTS race_results (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    driver_id INTEGER REFERENCES driver_profile(id),
    car_id INTEGER REFERENCES cars(id),
    starting_position INTEGER,
    finishing_position INTEGER,
    qualifying_time DECIMAL(10, 3),
    average_lap DECIMAL(10, 3),
    fastest_lap DECIMAL(10, 3),
    laps_completed INTEGER,
    laps_led INTEGER,
    incidents INTEGER,
    irating_change INTEGER,
    safety_rating_change DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_laps_session_id ON laps(session_id);
CREATE INDEX IF NOT EXISTS idx_laps_driver_id ON laps(driver_id);
CREATE INDEX IF NOT EXISTS idx_race_results_session_id ON race_results(session_id);
CREATE INDEX IF NOT EXISTS idx_race_results_driver_id ON race_results(driver_id);
EOF

# Create variables file for PostgreSQL module
cat > terraform/modules/postgres/variables.tf << 'EOF'
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
EOF

# Create outputs file for PostgreSQL module
cat > terraform/modules/postgres/outputs.tf << 'EOF'
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
EOF

echo "Terraform scaffolding complete!"