# File: python/collectors/iracing_collector_prometheus.py
import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime, timedelta

# Handle import dependencies gracefully
try:
    import pandas as pd
except ImportError:
    print("Error: pandas package is required. Install with: pip install pandas")
    sys.exit(1)
    
from dotenv import load_dotenv

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connector import PostgresConnector
from utils.prometheus_connector import PrometheusConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
    handlers=[
        logging.FileHandler("iracing_collector_prometheus.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("iracing_collector")

# Set up more verbose logging for debugging if needed
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    logger.debug("Debug mode enabled")

# Load environment variables
load_dotenv()

class iRacingCollector:
    """Collects data from iRacing API and stores it in PostgreSQL and Prometheus"""
    
    def __init__(self):
        """Initialize the collector with database connections and API credentials"""
        # Set up API credentials
        self.username = os.getenv("IRACING_USERNAME")
        self.password = os.getenv("IRACING_PASSWORD")
        
        if not self.username or not self.password:
            logger.error("iRacing credentials not found in environment variables")
            raise ValueError("iRacing credentials not found in environment variables")
        
        # Initialize database connections
        try:
            self.postgres = PostgresConnector()
            logger.debug("PostgreSQL connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection: {e}")
            logger.debug(f"PostgreSQL connection error details: {traceback.format_exc()}")
            raise
            
        try:
            self.prometheus = PrometheusConnector()
            logger.debug("Prometheus metrics server initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus metrics server: {e}")
            logger.debug(f"Prometheus initialization error details: {traceback.format_exc()}")
            raise
        
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
            logger.debug(f"pyracing client error details: {traceback.format_exc()}")
            raise
    
    async def authenticate(self):
        """Authenticate with iRacing API"""
        try:
            await self.ir.authenticate()
            logger.info("Successfully authenticated with iRacing API")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            logger.debug(f"Authentication error details: {traceback.format_exc()}")
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
            logger.debug(f"Career stats error details: {traceback.format_exc()}")
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
                try:
                    subsession_data = await self.ir.get_subsession_data(race.subsession_id)
                except Exception as e:
                    logger.error(f"Failed to get subsession data for {race.subsession_id}: {e}")
                    logger.debug(f"Subsession data error details: {traceback.format_exc()}")
                    continue
                
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
            logger.debug(f"Recent races error details: {traceback.format_exc()}")
            raise
    
    async def collect_telemetry(self, session_id=None):
        """Collect telemetry data from most recent session and store in Prometheus"""
        try:
            logger.info("Collecting telemetry data...")
            
            # If no session_id provided, get most recent one
            if not session_id:
                # This assumes integration with RaceLabs or similar
                # RaceLabs stores telemetry files locally
                telemetry_dir = os.getenv("RACELABS_TELEMETRY_DIR", "./telemetry")
                
                # Find the newest telemetry file
                try:
                    telemetry_files = [f for f in os.listdir(telemetry_dir) if f.endswith(".ibt")]
                    if not telemetry_files:
                        logger.warning("No telemetry files found in directory: " + telemetry_dir)
                        return False
                    
                    latest_file = max(telemetry_files, key=lambda f: os.path.getmtime(os.path.join(telemetry_dir, f)))
                    telemetry_path = os.path.join(telemetry_dir, latest_file)
                    logger.debug(f"Found telemetry file: {telemetry_path}")
                except FileNotFoundError:
                    logger.error(f"Telemetry directory not found: {telemetry_dir}")
                    return False
                except PermissionError:
                    logger.error(f"Permission denied accessing telemetry directory: {telemetry_dir}")
                    return False
                except Exception as e:
                    logger.error(f"Error finding telemetry files: {e}")
                    logger.debug(f"Telemetry file search error details: {traceback.format_exc()}")
                    return False
            else:
                # Logic to fetch telemetry for a specific session
                # This would depend on your specific setup with RaceLabs
                logger.warning("Fetching telemetry for specific session not implemented")
                return False
            
            # Parse telemetry file using irsdk or similar
            try:
                try:
                    import irsdk
                except ImportError:
                    logger.error("irsdk package not installed. Telemetry processing will be skipped.")
                    logger.info("Try installing irsdk with: pip install git+https://github.com/kutu/pyirsdk")
                    return False
                
                ir_sdk = irsdk.IRSDK()
                ir_sdk.startup(telemetry_path)
                
                if not ir_sdk.is_connected:
                    logger.error(f"Failed to load telemetry file: {telemetry_path}")
                    return False
                
                # Extract session info
                session_info = ir_sdk.session_info
                logger.debug(f"Loaded telemetry session info: {session_info.get('WeekendInfo', {}).get('TrackName', 'Unknown')}")
                
                # Get telemetry data at intervals
                telemetry_data = []
                sample_rate = int(os.getenv("TELEMETRY_SAMPLE_RATE", "10"))  # Sample every N ticks, configurable
                
                # Count total ticks for logging progress
                total_ticks = ir_sdk.session_data_ticks
                progress_interval = max(1, total_ticks // 10)  # Log progress at 10% intervals
                
                for i in range(0, total_ticks, sample_rate):
                    if i % progress_interval == 0:
                        logger.debug(f"Processing telemetry data: {i}/{total_ticks} ticks ({i/total_ticks*100:.1f}%)")
                    
                    try:
                        ir_sdk.seek_to_tick(i)
                        
                        # Extract relevant telemetry metrics
                        point = {
                            "timestamp": datetime.fromtimestamp(ir_sdk.session_time),
                            "lap": ir_sdk.get('Lap', 0),
                            "speed": ir_sdk.get('Speed', 0),
                            "rpm": ir_sdk.get('RPM', 0),
                            "throttle": ir_sdk.get('Throttle', 0),
                            "brake": ir_sdk.get('Brake', 0),
                            "gear": ir_sdk.get('Gear', 0),
                            "fuel_level": ir_sdk.get('FuelLevel', 0),
                            "fuel_use_per_hour": ir_sdk.get('FuelUsePerHour', 0),
                            "track_temp": ir_sdk.get('TrackTemp', 0),
                            "air_temp": ir_sdk.get('AirTemp', 0),
                            "lap_dist_pct": ir_sdk.get('LapDistPct', 0)
                        }
                        
                        # Add tire data if available
                        tire_keys = ['LFtempCM', 'RFtempCM', 'LRtempCM', 'RRtempCM']
                        if any(key in ir_sdk for key in tire_keys):
                            point.update({
                                "lf_temp": ir_sdk.get('LFtempCM', 0),
                                "rf_temp": ir_sdk.get('RFtempCM', 0),
                                "lr_temp": ir_sdk.get('LRtempCM', 0),
                                "rr_temp": ir_sdk.get('RRtempCM', 0)
                            })
                        
                        telemetry_data.append(point)
                    except Exception as e:
                        logger.warning(f"Error processing telemetry tick {i}: {e}")
                        if DEBUG_MODE:
                            logger.debug(f"Tick processing error details: {traceback.format_exc()}")
                        continue
                
                # Store in Prometheus
                try:
                    self.prometheus.write_telemetry_points(telemetry_data)
                    logger.info(f"Successfully updated {len(telemetry_data)} telemetry points in Prometheus")
                except Exception as e:
                    logger.error(f"Failed to write telemetry points to Prometheus: {e}")
                    logger.debug(f"Prometheus write error details: {traceback.format_exc()}")
                    return False
                
                return len(telemetry_data)
            
            finally:
                if 'ir_sdk' in locals() and hasattr(ir_sdk, 'is_connected') and ir_sdk.is_connected:
                    ir_sdk.shutdown()
                    logger.debug("iRacing SDK connection closed")
        
        except Exception as e:
            logger.error(f"Error collecting telemetry: {e}")
            logger.debug(f"Telemetry collection error details: {traceback.format_exc()}")
            raise
    
    def health_check(self):
        """Check the health of the collector and its dependencies"""
        health_status = {
            "status": "healthy",
            "checks": {
                "prometheus_server": "ok",
                "postgres_connection": "ok",
                "telemetry_directory": "ok"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Check Prometheus server
        if not self.prometheus.started:
            health_status["status"] = "unhealthy"
            health_status["checks"]["prometheus_server"] = "not running"
        
        # Check PostgreSQL connection
        try:
            self.postgres.check_connection()
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["postgres_connection"] = f"failed: {str(e)}"
        
        # Check telemetry directory
        telemetry_dir = os.getenv("RACELABS_TELEMETRY_DIR", "./telemetry")
        if not os.path.exists(telemetry_dir):
            health_status["status"] = "warning"
            health_status["checks"]["telemetry_directory"] = f"not found: {telemetry_dir}"
        elif not os.access(telemetry_dir, os.R_OK):
            health_status["status"] = "warning"
            health_status["checks"]["telemetry_directory"] = f"no read permission: {telemetry_dir}"
        
        logger.info(f"Health check: {health_status['status']}")
        return health_status
    
    def run_collection(self):
        """Run the full data collection process"""
        import asyncio
        
        async def main():
            # Authenticate
            retry_count = int(os.getenv("API_RETRY_COUNT", "3"))
            retry_delay = int(os.getenv("API_RETRY_DELAY", "5"))
            
            for attempt in range(1, retry_count + 1):
                try:
                    if not await self.authenticate():
                        if attempt < retry_count:
                            logger.warning(f"Authentication failed, retrying in {retry_delay} seconds (attempt {attempt}/{retry_count})")
                            await asyncio.sleep(retry_delay)
                            continue
                        logger.error(f"Authentication failed after {retry_count} attempts")
                        return False
                    break
                except Exception as e:
                    if attempt < retry_count:
                        logger.warning(f"Authentication error: {e}, retrying in {retry_delay} seconds (attempt {attempt}/{retry_count})")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Authentication error after {retry_count} attempts: {e}")
                        return False
            
            # Collection success flags
            career_stats_success = False
            race_success = False
            telemetry_success = False
            
            # Collect career stats with retry
            for attempt in range(1, retry_count + 1):
                try:
                    await self.collect_career_stats()
                    career_stats_success = True
                    break
                except Exception as e:
                    if attempt < retry_count:
                        logger.warning(f"Career stats collection error: {e}, retrying in {retry_delay} seconds (attempt {attempt}/{retry_count})")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Career stats collection failed after {retry_count} attempts: {e}")
            
            # Collect recent races with retry
            for attempt in range(1, retry_count + 1):
                try:
                    race_count = int(os.getenv("RACE_COLLECTION_COUNT", "20"))
                    await self.collect_recent_races(race_count)
                    race_success = True
                    break
                except Exception as e:
                    if attempt < retry_count:
                        logger.warning(f"Race collection error: {e}, retrying in {retry_delay} seconds (attempt {attempt}/{retry_count})")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Race collection failed after {retry_count} attempts: {e}")
            
            # Collect telemetry with retry
            for attempt in range(1, retry_count + 1):
                try:
                    await self.collect_telemetry()
                    telemetry_success = True
                    break
                except Exception as e:
                    if attempt < retry_count:
                        logger.warning(f"Telemetry collection error: {e}, retrying in {retry_delay} seconds (attempt {attempt}/{retry_count})")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Telemetry collection failed after {retry_count} attempts: {e}")
            
            # Consider success if at least one component succeeded
            return career_stats_success or race_success or telemetry_success
        
        # Run the async function
        try:
            success = asyncio.run(main())
            return success
        except Exception as e:
            logger.error(f"Unexpected error in collection process: {e}")
            logger.debug(f"Collection process error details: {traceback.format_exc()}")
            return False


if __name__ == "__main__":
    try:
        # Start the Prometheus metrics server
        collector = iRacingCollector()
        
        # Setup API endpoint for health checks
        from aiohttp import web
        import asyncio
        
        async def health_endpoint(request):
            """Health check API endpoint"""
            health_data = collector.health_check()
            return web.json_response(health_data)
        
        async def metrics_collection_task():
            """Background task for recurring data collection"""
            collection_interval = int(os.getenv("COLLECTION_INTERVAL", "600"))  # Default to 10 minutes
            
            while True:
                logger.info(f"Starting scheduled data collection (interval: {collection_interval}s)")
                try:
                    success = collector.run_collection()
                    if success:
                        logger.info("Scheduled data collection completed successfully")
                    else:
                        logger.error("Scheduled data collection failed")
                except Exception as e:
                    logger.error(f"Unexpected error in scheduled collection: {e}")
                    logger.debug(f"Scheduled collection error details: {traceback.format_exc()}")
                
                # Wait for next collection interval
                logger.debug(f"Waiting {collection_interval} seconds until next collection")
                await asyncio.sleep(collection_interval)
        
        # Keep the metrics server running and add health endpoint
        app = web.Application()
        app.router.add_get('/health', health_endpoint)
        
        # Initial data collection
        if collector.run_collection():
            logger.info("Initial data collection completed successfully")
            
            # Log metrics server information
            port = collector.prometheus.port
            logger.info(f"Prometheus metrics server running on port {port}")
            logger.info(f"Metrics available at http://localhost:{port}/metrics")
            logger.info(f"Health check available at http://localhost:8080/health")
            
            # Start the background collection task
            loop = asyncio.get_event_loop()
            loop.create_task(metrics_collection_task())
            
            # Start the web server for health endpoint
            web.run_app(app, port=8080)
            
        else:
            logger.error("Initial data collection failed")
            sys.exit(1)
            
    except ImportError as e:
        print(f"Error: Missing required dependencies. {e}")
        print("Make sure you have installed all required packages with:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Prometheus metrics server shutting down.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug(f"Startup error details: {traceback.format_exc()}")
        sys.exit(1)