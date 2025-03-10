# File: python/collectors/iracing_collector_prometheus_fixed.py
import os
import sys
import json
import time
import logging
import traceback
import base64
import hashlib
import hmac
import aiohttp
import asyncio
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
from utils.iracing_auth import iRacingAuth

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

# Load environment variables from the local .env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=dotenv_path)

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
        
        # Initialize iRacing Auth client
        self.ir = None
        
    async def connect_iracing_api(self):
        """Connect to the iRacing Data API"""
        try:
            self.ir = await iRacingAuth(self.username, self.password).initialize()
            logger.info("Successfully initialized iRacing Data API client")
            return True
        except Exception as e:
            logger.error(f"Error initializing iRacing Data API client: {e}")
            logger.debug(f"iRacing API client error details: {traceback.format_exc()}")
            return False
    
    async def authenticate(self):
        """Authenticate with iRacing API"""
        try:
            if not self.ir:
                success = await self.connect_iracing_api()
                return success
            
            # Ensure the auth client has a valid session
            success = await self.ir.ensure_authenticated()
            if success:
                logger.info("Successfully authenticated with iRacing API")
                return True
            else:
                logger.error("Failed to authenticate with iRacing API")
                return False
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            logger.debug(f"Authentication error details: {traceback.format_exc()}")
            return False
    
    async def collect_career_stats(self):
        """Collect career statistics and store in PostgreSQL"""
        try:
            logger.info("Collecting career statistics...")
            
            # Get customer ID from environment variable
            try:
                customer_id = int(os.getenv("IRACING_CUSTOMER_ID", "0"))
                if customer_id == 0:
                    # Try to use username as customer ID if it's numeric
                    try:
                        customer_id = int(self.username)
                        logger.debug(f"Using numeric username as customer ID: {customer_id}")
                    except ValueError:
                        logger.error("Could not determine customer ID. Set IRACING_CUSTOMER_ID env variable")
                        raise ValueError("Could not determine customer ID")
            except ValueError:
                logger.error("Invalid customer ID format. Must be an integer.")
                raise ValueError("Invalid customer ID format")
            
            # Get driver information
            driver_info = await self.ir.get_data(f"data/member/get", {"cust_id": customer_id})
            if not driver_info:
                logger.error("Failed to retrieve driver information")
                raise Exception("Failed to retrieve driver information")
            
            logger.debug(f"Retrieved driver info for customer ID: {customer_id}")
            
            # Get career stats
            career_stats = await self.ir.get_data(f"data/stats/member_career", {"cust_id": customer_id})
            if not career_stats:
                logger.error("Failed to retrieve career statistics")
                raise Exception("Failed to retrieve career statistics")
            
            # Get license info
            license_info = await self.ir.get_data(f"data/member/license", {"cust_id": customer_id})
            if not license_info:
                logger.error("Failed to retrieve license information")
                raise Exception("Failed to retrieve license information")
            
            # Process and store driver profile
            driver_data = {
                "iracing_id": customer_id,
                "name": driver_info.get("name", f"Driver {customer_id}"),
                "irating": driver_info.get("irating", 1350),
                "license_class": license_info.get("license_class", "Rookie"),
                "license_level": license_info.get("license_level", 1),
                "safety_rating": license_info.get("safety_rating", 2.5),
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
            
            # Get customer ID from environment variable
            try:
                customer_id = int(os.getenv("IRACING_CUSTOMER_ID", "0"))
                if customer_id == 0:
                    # Try to use username as customer ID if it's numeric
                    try:
                        customer_id = int(self.username)
                        logger.debug(f"Using numeric username as customer ID: {customer_id}")
                    except ValueError:
                        logger.error("Could not determine customer ID. Set IRACING_CUSTOMER_ID env variable")
                        raise ValueError("Could not determine customer ID")
            except ValueError:
                logger.error("Invalid customer ID format. Must be an integer.")
                raise ValueError("Invalid customer ID format")
            
            # Get driver info
            driver_info = await self.ir.get_data(f"data/member/get", {"cust_id": customer_id})
            if not driver_info:
                logger.error("Failed to retrieve driver information")
                raise Exception("Failed to retrieve driver information")
            
            # Get recent sessions from race guide
            recent_races = await self.ir.get_data(f"data/results/race_guide")
            if not recent_races or not recent_races.get("sessions"):
                logger.error("Failed to retrieve race guide data")
                raise Exception("Failed to retrieve race guide data")
            
            # Take only the sessions we need
            recent_races = recent_races.get("sessions", [])[:count]
            
            race_count = 0
            for race in recent_races:
                # Skip if the race is already in the database
                session_id = race.get("session_id")
                if not session_id:
                    logger.warning("Session ID missing in race guide data, skipping...")
                    continue
                    
                if self.postgres.session_exists(session_id):
                    logger.info(f"Session {session_id} already exists, skipping...")
                    continue
                
                # Get detailed subsession data
                subsession_id = race.get("subsession_id")
                if not subsession_id:
                    logger.warning(f"Subsession ID missing for session {session_id}, skipping...")
                    continue
                    
                try:
                    subsession_data = await self.ir.get_data(f"data/results/get", {"subsession_id": subsession_id})
                    if not subsession_data:
                        logger.error(f"Failed to get subsession data for {subsession_id}")
                        continue
                except Exception as e:
                    logger.error(f"Failed to get subsession data for {subsession_id}: {e}")
                    logger.debug(f"Subsession data error details: {traceback.format_exc()}")
                    continue
                
                # Extract track information
                track_data = {
                    "iracing_id": subsession_data.get("track", {}).get("track_id", 0),
                    "name": subsession_data.get("track", {}).get("track_name", "Unknown"),
                    "config": subsession_data.get("track", {}).get("config_name", ""),
                    "length_km": subsession_data.get("track", {}).get("track_length_km", 0),
                    "corners": subsession_data.get("track", {}).get("corners_per_lap", 0)
                }
                track_id = self.postgres.upsert_track(track_data)
                
                # Store session information
                session_data = {
                    "iracing_session_id": session_id,
                    "session_type": subsession_data.get("session_type", "Unknown"),
                    "track_id": track_id,
                    "start_time": subsession_data.get("start_time", datetime.now()),
                    "end_time": subsession_data.get("end_time", datetime.now()),
                    "weather_type": subsession_data.get("weather", {}).get("type", "Dynamic"),
                    "temp_track": subsession_data.get("weather", {}).get("track_temp", 0),
                    "temp_air": subsession_data.get("weather", {}).get("air_temp", 0)
                }
                session_id = self.postgres.insert_session(session_data)
                
                # Extract car information
                car_data = {
                    "iracing_id": subsession_data.get("car", {}).get("car_id", 0),
                    "name": subsession_data.get("car", {}).get("car_name", "Unknown"),
                    "class": subsession_data.get("car", {}).get("car_class", "Unknown")
                }
                car_id = self.postgres.upsert_car(car_data)
                
                # Store race results for the driver
                for result in subsession_data.get("results", []):
                    if result.get("cust_id") == customer_id:
                        result_data = {
                            "session_id": session_id,
                            "driver_id": self.postgres.get_driver_id(customer_id),
                            "car_id": car_id,
                            "starting_position": result.get("starting_position", 0),
                            "finishing_position": result.get("finishing_position", 0),
                            "qualifying_time": result.get("qualifying_time", 0),
                            "average_lap": result.get("average_lap_time", 0),
                            "fastest_lap": result.get("fastest_lap_time", 0),
                            "laps_completed": result.get("laps_completed", 0),
                            "laps_led": result.get("laps_led", 0),
                            "incidents": result.get("incidents", 0),
                            "irating_change": result.get("irating_change", 0),
                            "safety_rating_change": result.get("safety_rating_change", 0)
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
    
    async def close(self):
        """Close connections and clean up"""
        if self.ir:
            await self.ir.close()
    
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
            
            # Clean up connections
            await self.close()
            
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