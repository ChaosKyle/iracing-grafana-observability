FROM grafana/grafana:11.5.2

# Set Grafana env variables
ENV GF_INSTALL_PLUGINS="grafana-clock-panel,grafana-worldmap-panel,grafana-piechart-panel"
ENV GF_SECURITY_ADMIN_PASSWORD=admin
ENV GF_USERS_ALLOW_SIGN_UP=false
ENV GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s/grafana/
ENV GF_PATHS_PROVISIONING="/etc/grafana/provisioning"

# Copy dashboard provisioning configuration
COPY docker/dashboard/provisioning/dashboards /etc/grafana/provisioning/dashboards
COPY docker/dashboard/provisioning/datasources /etc/grafana/provisioning/datasources

# Copy dashboards
COPY dashboards /var/lib/grafana/dashboards
COPY terraform/modules/grafana/dashboards/*.json /var/lib/grafana/dashboards/

# Add custom entrypoint script
COPY docker/dashboard/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]