FROM grafana/grafana:latest

# Set Grafana env variables
ENV GF_INSTALL_PLUGINS="grafana-clock-panel,grafana-worldmap-panel,grafana-piechart-panel"
ENV GF_SECURITY_ADMIN_PASSWORD=admin
ENV GF_USERS_ALLOW_SIGN_UP=false
ENV GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s/grafana/
ENV GF_PATHS_PROVISIONING="/etc/grafana/provisioning"

# Switch to root user to install dependencies
USER root

# Install curl and postgresql-client for healthchecks
RUN apt-get update && \
    apt-get install -y curl postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy dashboard provisioning configuration
COPY docker/dashboard/provisioning/dashboards /etc/grafana/provisioning/dashboards
COPY docker/dashboard/provisioning/datasources /etc/grafana/provisioning/datasources

# Copy dashboards
RUN mkdir -p /var/lib/grafana/dashboards
COPY terraform/modules/grafana/dashboards/*.json /var/lib/grafana/dashboards/

# Add custom entrypoint script
COPY docker/dashboard/entrypoint.sh /usr/local/bin/custom-entrypoint.sh
RUN chmod +x /usr/local/bin/custom-entrypoint.sh

# Switch back to grafana user
USER grafana

ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]