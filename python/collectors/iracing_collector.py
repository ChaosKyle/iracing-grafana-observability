# File: python/collectors/iracing_collector.py
import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connector import PostgresConnector
from utils.influx_connector import InfluxConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("iracing_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("iracing_collector")

# Load environment variables
load_dotenv()

class iRacingCollector:
    """Collects data from iRacing API and stores it in PostgreSQL and InfluxDB"""
    
    def __init__(self):
        """Initialize the collector with database connections and API credentials"""
        # Set up API credentials
        self.username = os.getenv("IRACING_USERNAME")
        self.password = os.getenv("IRACING_PASSWORD")
        
        if not self.username or not self.password:
            logger.error("iRacing credentials not found in environment variables")
            raise ValueError("iRacing credentials not found in environment variables")
        
        # Initialize database connections
        self.postgres = PostgresConnector()
        self.influx = InfluxConnector()
        
        # Import pyracing here to handle any import issues gracefully
        try:
            import pyracing
            self.ir = pyracing.Client(self.username, self.password)
            logger.info("Successfully initialized pyracing client")
        except ImportError:
            logger.error("Failed to import pyracing. Make sure it's installed.")
            raise
        except Exception as e:
            logger.error(f"Error initializing pyracing client: {e}")
            raise
    
    async def authenticate(self):
        """Authenticate with iRacing API"""
        try:
            await self.ir.authenticate()
            logger.info("Successfully authenticated with iRacing API")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    async def collect_career_stats(self):
        """Collect career statistics and store in PostgreSQL"""
        try:
            logger.info("Collecting career statistics...")
            
            # Get driver info
            driver_info = await self.ir.get_driver_info()
            customer_id = driver_info.cust_id
            
            # Get career stats
            career_stats = await self.ir.get_career_stats(customer_id)
            
            # Get license info
            license_info = await self.ir.get_license_info(customer_id)
            
            # Process and store driver profile
            driver_data = {
                "iracing_id": customer_id,
                "name": f"{driver_info.first_name} {driver_info.last_name}",
                "irating": driver_info.irating,
                "license_class": license_info.license_class,
                "license_level": license_info.license_level,
                "safety_rating": license_info.safety_rating,
                "updated_at": datetime.now()
            }
            
            # Update or insert driver profile
            self.postgres.upsert_driver_profile(driver_data)
            logger.info(f"Stored driver profile for {driver_data['name']}")
            
            return driver_data
        except Exception as e:
            logger.error(f"Error collecting career stats: {e}")
            raise
    
    async def collect_recent_races(self, count=10):
        """Collect recent race results and store in PostgreSQL"""
        try:
            logger.info(f"Collecting {count} recent races...")
            
            # Get recent race results
            driver_info = await self.ir.get_driver_info()
            customer_id = driver_info.cust_id
            
            # Get recent sessions
            recent_races = await self.ir.get_race_guide_results(customer_id, count)
            
            race_count = 0
            for race in recent_races:
                # Skip if the race is already in the database
                if self.postgres.session_exists(race.session_id):
                    logger.info(f"Session {race.session_id} already exists, skipping...")
                    continue
                
                # Get detailed subsession data
                subsession_data = await self.ir.get_subsession_data(race.subsession_id)
                
                # Store track information
                track_data = {
                    "iracing_id": subsession_data.track.track_id,
                    "name": subsession_data.track.track_name,
                    "config": subsession_data.track.config_name,
                    "length_km": subsession_data.track.track_length_km,
                    "corners": subsession_data.track.corners_per_lap
                }
                track_id = self.postgres.upsert_track(track_data)
                
                # Store session information
                session_data = {
                    "iracing_session_id": race.session_id,
                    "session_type": subsession_data.session_type,
                    "track_id": track_id,
                    "start_time": subsession_data.start_time,
                    "end_time": subsession_data.end_time,
                    "weather_type": subsession_data.weather.type,
                    "temp_track": subsession_data.weather.track_temp,
                    "temp_air": subsession_data.weather.air_temp
                }
                session_id = self.postgres.insert_session(session_data)
                
                # Get car info and store it
                car_data = {
                    "iracing_id": subsession_data.car.car_id,
                    "name": subsession_data.car.car_name,
                    "class": subsession_data.car.car_class
                }
                car_id = self.postgres.upsert_car(car_data)
                
                # Store race results for the driver
                for result in subsession_data.results:
                    if result.cust_id == customer_id:
                        result_data = {
                            "session_id": session_id,
                            "driver_id": self.postgres.get_driver_id(customer_id),
                            "car_id": car_id,
                            "starting_position": result.starting_position,
                            "finishing_position": result.finishing_position,
                            "qualifying_time": result.qualifying_time,
                            "average_lap": result.average_lap_time,
                            "fastest_lap": result.fastest_lap_time,
                            "laps_completed": result.laps_completed,
                            "laps_led": result.laps_led,
                            "incidents": result.incidents,
                            "irating_change": result.irating_change,
                            "safety_rating_change": result.safety_rating_change
                        }
                        self.postgres.insert_race_result(result_data)
                        break
                
                race_count += 1
                logger.info(f"Stored race {race_count}/{count}: {session_data['session_type']} at {track_data['name']}")
            
            logger.info(f"Successfully collected {race_count} new races")
            return race_count
        except Exception as e:
            logger.error(f"Error collecting recent races: {e}")
            raise
    
    async def collect_telemetry(self, session_id=None):
        """Collect telemetry data from most recent session and store in InfluxDB"""
        try:
            logger.info("Collecting telemetry data...")
            
            # If no session_id provided, get most recent one
            if not session_id:
                # This assumes integration with RaceLabs or similar
                # RaceLabs stores telemetry files locally
                telemetry_dir = os.getenv("RACELABS_TELEMETRY_DIR", "./telemetry")
                
                # Find the newest telemetry file
                telemetry_files = [f for f in os.listdir(telemetry_dir) if f.endswith(".ibt")]
                if not telemetry_files:
                    logger.warning("No telemetry files found")
                    return False
                
                latest_file = max(telemetry_files, key=lambda f: os.path.getmtime(os.path.join(telemetry_dir, f)))
                telemetry_path = os.path.join(telemetry_dir, latest_file)
            else:
                # Logic to fetch telemetry for a specific session
                # This would depend on your specific setup with RaceLabs
                logger.warning("Fetching telemetry for specific session not implemented")
                return False
            
            # Parse telemetry file using irsdk or similar
            try:
                import irsdk
                ir_sdk = irsdk.IRSDK()
                ir_sdk.startup(telemetry_path)
                
                if not ir_sdk.is_connected:
                    logger.error("Failed to load telemetry file")
                    return False
                
                # Extract session info
                session_info = ir_sdk.session_info
                
                # Get telemetry data at intervals
                telemetry_data = []
                for i in range(0, ir_sdk.session_data_ticks, 10):  # Sample every 10 ticks
                    ir_sdk.seek_to_tick(i)
                    
                    # Extract relevant telemetry metrics
                    point = {
                        "timestamp": datetime.fromtimestamp(ir_sdk.session_time),
                        "lap": ir_sdk['Lap'],
                        "speed": ir_sdk['Speed'],
                        "rpm": ir_sdk['RPM'],
                        "throttle": ir_sdk['Throttle'],
                        "brake": ir_sdk['Brake'],
                        "gear": ir_sdk['Gear'],
                        "fuel_level": ir_sdk['FuelLevel'],
                        "fuel_use_per_hour": ir_sdk['FuelUsePerHour'],
                        "track_temp": ir_sdk['TrackTemp'],
                        "air_temp": ir_sdk['AirTemp'],
                        "lap_dist_pct": ir_sdk['LapDistPct']
                    }
                    
                    # Add tire data if available
                    if all(key in ir_sdk for key in ['LFtempCM', 'RFtempCM', 'LRtempCM', 'RRtempCM']):
                        point.update({
                            "lf_temp": ir_sdk['LFtempCM'],
                            "rf_temp": ir_sdk['RFtempCM'],
                            "lr_temp": ir_sdk['LRtempCM'],
                            "rr_temp": ir_sdk['RRtempCM']
                        })
                    
                    telemetry_data.append(point)
                
                # Store in InfluxDB
                self.influx.write_telemetry_points(telemetry_data)
                
                logger.info(f"Successfully stored {len(telemetry_data)} telemetry points")
                return len(telemetry_data)
            
            finally:
                if 'ir_sdk' in locals() and ir_sdk.is_connected:
                    ir_sdk.shutdown()
        
        except Exception as e:
            logger.error(f"Error collecting telemetry: {e}")
            raise
    
    def run_collection(self):
        """Run the full data collection process"""
        import asyncio
        
        async def main():
            # Authenticate
            if not await self.authenticate():
                return False
            
            # Collect career stats
            await self.collect_career_stats()
            
            # Collect recent races
            await self.collect_recent_races(20)
            
            # Collect telemetry
            await self.collect_telemetry()
            
            return True
        
        # Run the async function
        success = asyncio.run(main())
        return success


if __name__ == "__main__":
    collector = iRacingCollector()
    if collector.run_collection():
        logger.info("Data collection completed successfully")
    else:
        logger.error("Data collection failed")
        sys.exit(1)