#!/usr/bin/env python3
# File: python/utils/prometheus_connector.py
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Counter

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("prometheus_connector")

class PrometheusConnector:
    """Connector class for Prometheus metrics"""
    
    def __init__(self):
        """Initialize the Prometheus metrics exporter"""
        self.port = int(os.getenv("PROMETHEUS_PORT", "8000"))
        self.metrics = {}
        self.started = False
        self.start_server()
        logger.info(f"Prometheus metrics server started on port {self.port}")
    
    def start_server(self):
        """Start the Prometheus HTTP server if not already running"""
        if not self.started:
            try:
                start_http_server(self.port)
                self.started = True
                logger.info(f"Prometheus metrics server started on port {self.port}")
            except Exception as e:
                logger.error(f"Failed to start Prometheus metrics server: {e}")
                raise
    
    def _get_or_create_gauge(self, name, description=""):
        """Get an existing gauge or create a new one"""
        if name not in self.metrics:
            self.metrics[name] = Gauge(name, description)
        return self.metrics[name]
    
    def write_telemetry_points(self, telemetry_data):
        """Write telemetry data points as Prometheus metrics"""
        try:
            for point_data in telemetry_data:
                # Remove timestamp if present, as Prometheus handles timestamps automatically
                point_data.pop("timestamp", None)
                
                # Get lap for use in labels
                lap = point_data.pop("lap", "unknown")
                
                # Add all fields as separate metrics
                for key, value in point_data.items():
                    # Skip None values
                    if value is None:
                        continue
                    
                    # Create a sanitized metric name (Prometheus requires a specific format)
                    metric_name = f"iracing_telemetry_{key}".replace(".", "_").replace("-", "_").lower()
                    
                    # Get or create the gauge
                    gauge = self._get_or_create_gauge(metric_name, f"iRacing telemetry metric: {key}")
                    
                    # Set the value with lap as a label
                    if isinstance(value, (int, float)):
                        gauge.labels(lap=str(lap)).set(float(value))
            
            logger.info(f"Successfully updated {len(telemetry_data)} Prometheus metrics")
            return True
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
            raise
    
    # Note: Prometheus doesn't support direct querying from this client
    # Querying is done through Grafana directly from the Prometheus server