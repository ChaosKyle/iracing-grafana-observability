#!/usr/bin/env python3
# File: python/utils/prometheus_connector.py
import os
import time
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Counter, Histogram

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
        
        # Create core metrics for monitoring the collector itself
        self.collector_health = Gauge('iracing_collector_health', 'Health status of the iRacing collector')
        self.collection_duration = Gauge('iracing_collection_duration_seconds', 'Duration of data collection operations')
        self.collection_errors = Counter('iracing_collection_errors_total', 'Total number of collection errors', ['component'])
        self.api_requests = Counter('iracing_api_requests_total', 'Total number of API requests', ['endpoint', 'status'])
        
        # Start the metrics server
        self.start_server()
        logger.info(f"Prometheus metrics server started on port {self.port}")
        
        # Set collector as healthy by default
        self.collector_health.set(1)
    
    def start_server(self):
        """Start the Prometheus HTTP server if not already running"""
        if not self.started:
            try:
                start_http_server(self.port)
                self.started = True
                logger.info(f"Prometheus metrics server started on port {self.port}")
            except Exception as e:
                logger.error(f"Failed to start Prometheus metrics server: {e}")
                logger.debug(f"Prometheus server error details: {traceback.format_exc()}")
                raise
    
    def check_connection(self):
        """Check if the Prometheus metrics server is running"""
        if not self.started:
            raise RuntimeError("Prometheus metrics server is not running")
        return True
    
    def _get_or_create_gauge(self, name, description="", labels=None):
        """Get an existing gauge or create a new one"""
        if name not in self.metrics:
            if labels:
                self.metrics[name] = Gauge(name, description, labels)
            else:
                self.metrics[name] = Gauge(name, description)
        return self.metrics[name]
    
    def record_api_request(self, endpoint, success=True):
        """Record an API request with its status"""
        status = "success" if success else "failure"
        self.api_requests.labels(endpoint=endpoint, status=status).inc()
    
    def record_collection_error(self, component):
        """Record a collection error for a specific component"""
        self.collection_errors.labels(component=component).inc()
        # Also set health to 0 (unhealthy)
        self.collector_health.set(0)
    
    def record_collection_duration(self, duration_seconds):
        """Record the duration of a collection operation"""
        self.collection_duration.set(duration_seconds)
    
    def set_health_status(self, healthy=True):
        """Set the health status of the collector"""
        self.collector_health.set(1 if healthy else 0)
    
    def write_telemetry_points(self, telemetry_data):
        """Write telemetry data points as Prometheus metrics"""
        try:
            start_time = time.time()
            points_processed = 0
            
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
                    gauge = self._get_or_create_gauge(metric_name, f"iRacing telemetry metric: {key}", ["lap"])
                    
                    # Set the value with lap as a label
                    if isinstance(value, (int, float)):
                        gauge.labels(lap=str(lap)).set(float(value))
                        points_processed += 1
            
            # Record metrics about this operation
            processing_time = time.time() - start_time
            self.record_collection_duration(processing_time)
            
            logger.info(f"Successfully updated {points_processed} Prometheus metrics in {processing_time:.2f} seconds")
            return True
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
            logger.debug(f"Prometheus metrics update error details: {traceback.format_exc()}")
            self.record_collection_error("telemetry")
            raise
    
    # Note: Prometheus doesn't support direct querying from this client
    # Querying is done through Grafana directly from the Prometheus server