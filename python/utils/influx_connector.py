#!/usr/bin/env python3
# File: python/utils/influx_connector.py
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("influx_connector")

class InfluxConnector:
    """Connector class for InfluxDB operations"""
    
    def __init__(self):
        """Initialize the InfluxDB connection"""
        self.url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
        self.token = os.getenv("INFLUXDB_TOKEN")
        self.org = os.getenv("INFLUXDB_ORG", "iracing")
        self.bucket = os.getenv("INFLUXDB_BUCKET", "iracing_telemetry")
        
        if not self.token:
            logger.error("InfluxDB token not found in environment variables")
            raise ValueError("InfluxDB token not found in environment variables")
        
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            logger.info("Successfully connected to InfluxDB")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            raise
    
    def __del__(self):
        """Close the connection when the object is destroyed"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
    
    def write_telemetry_points(self, telemetry_data):
        """Write telemetry data points to InfluxDB"""
        try:
            points = []
            for point_data in telemetry_data:
                # Create a Point
                point = Point("telemetry")
                
                # Add timestamp
                timestamp = point_data.pop("timestamp", datetime.now())
                
                # Add tags for indexing
                if "lap" in point_data:
                    point = point.tag("lap", str(point_data.pop("lap")))
                
                # Add all fields
                for key, value in point_data.items():
                    # Skip None values
                    if value is None:
                        continue
                    
                    # Add appropriate type of field
                    if isinstance(value, bool):
                        point = point.field(key, value)
                    elif isinstance(value, (int, float)):
                        point = point.field(key, float(value))
                    else:
                        point = point.field(key, str(value))
                
                # Set timestamp and add to points list
                point = point.time(timestamp)
                points.append(point)
            
            # Write all points
            self.write_api.write(bucket=self.bucket, record=points)
            logger.info(f"Successfully wrote {len(points)} points to InfluxDB")
            return True
        except Exception as e:
            logger.error(f"Error writing telemetry points to InfluxDB: {e}")
            raise
    
    def query_recent_telemetry(self, minutes=30):
        """Query recent telemetry data"""
        try:
            flux_query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -{minutes}m)
                |> filter(fn: (r) => r._measurement == "telemetry")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
            
            result = self.query_api.query(query=flux_query, org=self.org)
            
            # Process the result into a more usable format
            data = []
            for table in result:
                for record in table.records:
                    data.append(record.values)
            
            return data
        except Exception as e:
            logger.error(f"Error querying recent telemetry: {e}")
            return []
    
    def query_lap_telemetry(self, lap_number):
        """Query telemetry data for a specific lap"""
        try:
            flux_query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -24h)
                |> filter(fn: (r) => r._measurement == "telemetry")
                |> filter(fn: (r) => r.lap == "{lap_number}")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> sort(columns: ["_time"], desc: false)
            '''
            
            result = self.query_api.query(query=flux_query, org=self.org)
            
            # Process the result into a more usable format
            data = []
            for table in result:
                for record in table.records:
                    data.append(record.values)
            
            return data
        except Exception as e:
            logger.error(f"Error querying lap telemetry: {e}")
            return []