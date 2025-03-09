#!/usr/bin/env python3
# File: python/utils/prometheus_connector.py
import os
import time
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Counter, Histogram

# Load environment variables from the local .env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=dotenv_path)

# Configure logging
logger = logging.getLogger("prometheus_connector")

class PrometheusConnector:
    """Connector class for Prometheus metrics"""
    
    def __init__(self):
        """Initialize the Prometheus metrics server"""
        # Get Prometheus port (handle incorrectly set environment variables)
        prometheus_port = os.getenv("PROMETHEUS_PORT", "9090")
        try:
            prometheus_port = int(prometheus_port)
        except ValueError:
            # If the port is incorrectly set to a string like "localhost", use the default
            logger.warning(f"Invalid Prometheus port: {prometheus_port}, using default 9090")
            prometheus_port = 9090
            
        self.port = prometheus_port
        self.started = False
        
        # Initialize metrics
        self._setup_metrics()
        
        # Start metrics server
        try:
            start_http_server(self.port)
            self.started = True
            logger.info(f"Prometheus metrics server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus metrics server: {e}")
            logger.error(f"Prometheus server error details: {traceback.format_exc()}")
            raise
    
    def _setup_metrics(self):
        """Set up Prometheus metrics"""
        # Driver metrics
        self.irating = Gauge('iracing_driver_irating', 'Driver iRating', ['driver_id', 'driver_name'])
        self.safety_rating = Gauge('iracing_driver_safety_rating', 'Driver Safety Rating', ['driver_id', 'driver_name', 'license_class'])
        
        # Race metrics
        self.race_count = Counter('iracing_race_count_total', 'Total number of races', ['driver_id'])
        self.race_position = Histogram('iracing_race_finishing_position', 'Race finishing position', ['driver_id', 'track', 'car'])
        self.qualifying_position = Histogram('iracing_qualifying_position', 'Qualifying position', ['driver_id', 'track', 'car'])
        self.incident_count = Counter('iracing_incident_count_total', 'Total number of incidents', ['driver_id'])
        
        # Lap metrics
        self.lap_time = Histogram('iracing_lap_time_seconds', 'Lap time in seconds', ['driver_id', 'track', 'car'], 
                                  buckets=(60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200))
        self.lap_count = Counter('iracing_lap_count_total', 'Total number of laps', ['driver_id', 'track', 'car'])
        
        # Telemetry metrics
        self.speed = Gauge('iracing_telemetry_speed', 'Car speed in m/s', ['driver_id', 'car', 'track', 'lap'])
        self.throttle = Gauge('iracing_telemetry_throttle', 'Throttle position (0-1)', ['driver_id', 'car', 'track', 'lap'])
        self.brake = Gauge('iracing_telemetry_brake', 'Brake position (0-1)', ['driver_id', 'car', 'track', 'lap'])
        self.fuel_level = Gauge('iracing_telemetry_fuel_level', 'Fuel level in liters', ['driver_id', 'car', 'track', 'lap'])
        self.fuel_use = Gauge('iracing_telemetry_fuel_use_per_hour', 'Fuel use per hour in liters', ['driver_id', 'car', 'track', 'lap'])
        self.rpm = Gauge('iracing_telemetry_rpm', 'Engine RPM', ['driver_id', 'car', 'track', 'lap'])
        self.gear = Gauge('iracing_telemetry_gear', 'Current gear', ['driver_id', 'car', 'track', 'lap'])
        
        # Tire temperatures
        self.tire_temp_lf = Gauge('iracing_telemetry_tire_temp_lf', 'Left front tire temperature (C)', ['driver_id', 'car', 'track', 'lap'])
        self.tire_temp_rf = Gauge('iracing_telemetry_tire_temp_rf', 'Right front tire temperature (C)', ['driver_id', 'car', 'track', 'lap'])
        self.tire_temp_lr = Gauge('iracing_telemetry_tire_temp_lr', 'Left rear tire temperature (C)', ['driver_id', 'car', 'track', 'lap'])
        self.tire_temp_rr = Gauge('iracing_telemetry_tire_temp_rr', 'Right rear tire temperature (C)', ['driver_id', 'car', 'track', 'lap'])
        
        # System metrics
        self.system_up = Gauge('iracing_collector_up', 'Whether the collector is running (1 for yes, 0 for no)')
        self.system_up.set(1)  # Set to 1 when the collector starts
        self.last_collection_timestamp = Gauge('iracing_collector_last_collection_timestamp', 'Timestamp of the last data collection')
        self.last_collection_success = Gauge('iracing_collector_last_collection_success', 'Whether the last collection was successful (1 for yes, 0 for no)')
        self.last_collection_duration = Gauge('iracing_collector_last_collection_duration_seconds', 'Duration of the last collection in seconds')
    
    def update_driver_metrics(self, driver_data):
        """Update driver-related metrics"""
        try:
            driver_id = str(driver_data.get('iracing_id', 'unknown'))
            driver_name = driver_data.get('name', 'Unknown Driver')
            
            # Update iRating
            if 'irating' in driver_data:
                self.irating.labels(driver_id=driver_id, driver_name=driver_name).set(driver_data['irating'])
            
            # Update Safety Rating
            if 'safety_rating' in driver_data:
                license_class = driver_data.get('license_class', 'R')
                self.safety_rating.labels(
                    driver_id=driver_id, 
                    driver_name=driver_name, 
                    license_class=license_class
                ).set(driver_data['safety_rating'])
                
            logger.debug(f"Updated driver metrics for {driver_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating driver metrics: {e}")
            logger.error(f"Driver metrics update error details: {traceback.format_exc()}")
            return False
    
    def update_race_metrics(self, race_data, driver_info):
        """Update race-related metrics"""
        try:
            driver_id = str(driver_info.get('iracing_id', 'unknown'))
            track_name = race_data.get('track_name', 'Unknown Track')
            if race_data.get('track_config'):
                track_name += f" ({race_data['track_config']})"
            
            car_name = race_data.get('car_name', 'Unknown Car')
            
            # Update race count
            self.race_count.labels(driver_id=driver_id).inc()
            
            # Update positions
            if 'finishing_position' in race_data:
                self.race_position.labels(
                    driver_id=driver_id, 
                    track=track_name, 
                    car=car_name
                ).observe(race_data['finishing_position'])
            
            if 'starting_position' in race_data:
                self.qualifying_position.labels(
                    driver_id=driver_id, 
                    track=track_name, 
                    car=car_name
                ).observe(race_data['starting_position'])
            
            # Update incidents
            if 'incidents' in race_data and race_data['incidents'] > 0:
                self.incident_count.labels(driver_id=driver_id).inc(race_data['incidents'])
            
            # Update laps
            if 'laps_completed' in race_data and race_data['laps_completed'] > 0:
                self.lap_count.labels(
                    driver_id=driver_id, 
                    track=track_name, 
                    car=car_name
                ).inc(race_data['laps_completed'])
            
            logger.debug(f"Updated race metrics for driver {driver_id} at {track_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating race metrics: {e}")
            logger.error(f"Race metrics update error details: {traceback.format_exc()}")
            return False
    
    def update_lap_metrics(self, lap_data, driver_info, track_info, car_info):
        """Update lap-related metrics"""
        try:
            driver_id = str(driver_info.get('iracing_id', 'unknown'))
            track_name = track_info.get('name', 'Unknown Track')
            if track_info.get('config'):
                track_name += f" ({track_info['config']})"
            
            car_name = car_info.get('name', 'Unknown Car')
            
            # Update lap time if valid
            if 'lap_time' in lap_data and lap_data.get('valid_lap', True):
                # Convert from milliseconds to seconds
                lap_time_seconds = lap_data['lap_time'] / 1000.0
                self.lap_time.labels(
                    driver_id=driver_id, 
                    track=track_name, 
                    car=car_name
                ).observe(lap_time_seconds)
            
            # Increment lap count
            self.lap_count.labels(
                driver_id=driver_id, 
                track=track_name, 
                car=car_name
            ).inc()
            
            logger.debug(f"Updated lap metrics for driver {driver_id} at {track_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating lap metrics: {e}")
            logger.error(f"Lap metrics update error details: {traceback.format_exc()}")
            return False
    
    def write_telemetry_points(self, telemetry_data):
        """Write telemetry data to Prometheus metrics"""
        try:
            points_written = 0
            driver_id = "current"  # Default since we don't have driver ID in telemetry
            car_name = "current"  # Default
            track_name = "current"  # Default
            
            for point in telemetry_data:
                lap = point.get('lap', 0)
                lap_str = str(lap)
                
                # Update basic telemetry metrics
                if 'speed' in point:
                    self.speed.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['speed'])
                
                if 'throttle' in point:
                    self.throttle.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['throttle'])
                
                if 'brake' in point:
                    self.brake.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['brake'])
                
                if 'fuel_level' in point:
                    self.fuel_level.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['fuel_level'])
                
                if 'fuel_use_per_hour' in point:
                    self.fuel_use.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['fuel_use_per_hour'])
                
                if 'rpm' in point:
                    self.rpm.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['rpm'])
                
                if 'gear' in point:
                    self.gear.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['gear'])
                
                # Update tire temperature metrics if available
                if 'lf_temp' in point:
                    self.tire_temp_lf.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['lf_temp'])
                
                if 'rf_temp' in point:
                    self.tire_temp_rf.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['rf_temp'])
                
                if 'lr_temp' in point:
                    self.tire_temp_lr.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['lr_temp'])
                
                if 'rr_temp' in point:
                    self.tire_temp_rr.labels(driver_id=driver_id, car=car_name, track=track_name, lap=lap_str).set(point['rr_temp'])
                
                points_written += 1
            
            # Update collection metrics
            self.last_collection_timestamp.set(time.time())
            self.last_collection_success.set(1)
            
            logger.info(f"Successfully wrote {points_written} telemetry points to Prometheus")
            return points_written
        except Exception as e:
            logger.error(f"Error writing telemetry points: {e}")
            logger.error(f"Telemetry points write error details: {traceback.format_exc()}")
            self.last_collection_success.set(0)
            return 0
    
    def record_collection_metrics(self, success, duration_seconds):
        """Record metrics about the collection process itself"""
        try:
            self.last_collection_timestamp.set(time.time())
            self.last_collection_success.set(1 if success else 0)
            self.last_collection_duration.set(duration_seconds)
            logger.debug(f"Updated collection metrics: success={success}, duration={duration_seconds}s")
            return True
        except Exception as e:
            logger.error(f"Error updating collection metrics: {e}")
            return False