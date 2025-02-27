FROM grafana/grafana:9.3.2

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
RUN mkdir -p /var/lib/grafana/dashboards
COPY terraform/modules/grafana/dashboards/*.json /var/lib/grafana/dashboards/

# Add custom entrypoint script
COPY docker/dashboard/entrypoint.sh /usr/local/bin/custom-entrypoint.sh
USER root
RUN chmod +x /usr/local/bin/custom-entrypoint.sh
USER grafana

ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]