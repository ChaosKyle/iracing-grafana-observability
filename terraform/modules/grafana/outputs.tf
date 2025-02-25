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
