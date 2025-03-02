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
    local = {
      source  = "hashicorp/local"
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
  prometheus_url      = module.prometheus.prometheus_url
  postgres_host       = module.postgres.postgres_host
  postgres_port       = module.postgres.postgres_port
  postgres_user       = var.postgres_user
  postgres_password   = var.postgres_password
  postgres_database   = var.postgres_database
}

module "prometheus" {
  source = "../../modules/prometheus"
  
  prometheus_data_path = var.prometheus_data_path
  prometheus_port      = var.prometheus_port
}

module "postgres" {
  source = "../../modules/postgres"
  
  postgres_user       = var.postgres_user
  postgres_password   = var.postgres_password
  postgres_database   = var.postgres_database
}
