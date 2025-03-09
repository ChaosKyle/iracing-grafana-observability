#!/usr/bin/env python3
# File: python/utils/db_connector.py
import os
import logging
import traceback
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("postgres_connector")

class PostgresConnector:
    """Connector class for PostgreSQL database operations"""
    
    def __init__(self):
        """Initialize the PostgreSQL connection"""
        self.conn_params = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "database": os.getenv("POSTGRES_DB", "iracing_data")
        }
        
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.conn.autocommit = False
            logger.info("Successfully connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            logger.error(f"PostgreSQL connection error details: {traceback.format_exc()}")
            raise
    
    def __del__(self):
        """Close the connection when the object is destroyed"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            
    def check_connection(self):
        """Check if the PostgreSQL connection is active"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    return True
                else:
                    raise RuntimeError("PostgreSQL connection test failed")
        except Exception as e:
            logger.error(f"PostgreSQL connection check failed: {e}")
            logger.error(f"Connection check error details: {traceback.format_exc()}")
            # Try to reconnect
            try:
                self.conn = psycopg2.connect(**self.conn_params)
                self.conn.autocommit = False
                logger.info("Successfully reconnected to PostgreSQL")
                return True
            except Exception as reconnect_error:
                logger.error(f"Failed to reconnect to PostgreSQL: {reconnect_error}")
                raise RuntimeError(f"PostgreSQL connection is down: {e}")
    
    def session_exists(self, iracing_session_id):
        """Check if a session already exists in the database"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM sessions WHERE iracing_session_id = %s",
                    (iracing_session_id,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if session exists: {e}")
            logger.error(f"Session check error details: {traceback.format_exc()}")
            self.conn.rollback()
            return False
    
    def upsert_track(self, track_data):
        """Insert or update track information and return the track ID"""
        try:
            with self.conn.cursor() as cursor:
                # Check if track exists
                cursor.execute(
                    "SELECT id FROM tracks WHERE iracing_id = %s",
                    (track_data["iracing_id"],)
                )
                result = cursor.fetchone()
                
                if result:
                    # Update existing track
                    track_id = result[0]
                    cursor.execute(
                        """
                        UPDATE tracks
                        SET name = %s, config = %s, length_km = %s, corners = %s, updated_at = NOW()
                        WHERE id = %s
                        """,
                        (
                            track_data["name"],
                            track_data["config"],
                            track_data["length_km"],
                            track_data["corners"],
                            track_id
                        )
                    )
                else:
                    # Insert new track
                    cursor.execute(
                        """
                        INSERT INTO tracks (iracing_id, name, config, length_km, corners)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            track_data["iracing_id"],
                            track_data["name"],
                            track_data["config"],
                            track_data["length_km"],
                            track_data["corners"]
                        )
                    )
                    track_id = cursor.fetchone()[0]
                
                self.conn.commit()
                return track_id
        except Exception as e:
            logger.error(f"Error upserting track: {e}")
            logger.error(f"Track upsert error details: {traceback.format_exc()}")
            self.conn.rollback()
            raise
    
    def upsert_car(self, car_data):
        """Insert or update car information and return the car ID"""
        try:
            with self.conn.cursor() as cursor:
                # Check if car exists
                cursor.execute(
                    "SELECT id FROM cars WHERE iracing_id = %s",
                    (car_data["iracing_id"],)
                )
                result = cursor.fetchone()
                
                if result:
                    # Update existing car
                    car_id = result[0]
                    cursor.execute(
                        """
                        UPDATE cars
                        SET name = %s, class = %s, updated_at = NOW()
                        WHERE id = %s
                        """,
                        (
                            car_data["name"],
                            car_data["class"],
                            car_id
                        )
                    )
                else:
                    # Insert new car
                    cursor.execute(
                        """
                        INSERT INTO cars (iracing_id, name, class)
                        VALUES (%s, %s, %s)
                        RETURNING id
                        """,
                        (
                            car_data["iracing_id"],
                            car_data["name"],
                            car_data["class"]
                        )
                    )
                    car_id = cursor.fetchone()[0]
                
                self.conn.commit()
                return car_id
        except Exception as e:
            logger.error(f"Error upserting car: {e}")
            logger.error(f"Car upsert error details: {traceback.format_exc()}")
            self.conn.rollback()
            raise
    
    def upsert_driver_profile(self, driver_data):
        """Insert or update driver profile and return the driver ID"""
        try:
            with self.conn.cursor() as cursor:
                # Check if driver exists
                cursor.execute(
                    "SELECT id FROM driver_profile WHERE iracing_id = %s",
                    (driver_data["iracing_id"],)
                )
                result = cursor.fetchone()
                
                if result:
                    # Update existing driver
                    driver_id = result[0]
                    cursor.execute(
                        """
                        UPDATE driver_profile
                        SET name = %s, irating = %s, license_class = %s, 
                            license_level = %s, safety_rating = %s, updated_at = NOW()
                        WHERE id = %s
                        """,
                        (
                            driver_data["name"],
                            driver_data["irating"],
                            driver_data["license_class"],
                            driver_data["license_level"],
                            driver_data["safety_rating"],
                            driver_id
                        )
                    )
                else:
                    # Insert new driver
                    cursor.execute(
                        """
                        INSERT INTO driver_profile 
                        (iracing_id, name, irating, license_class, license_level, safety_rating)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            driver_data["iracing_id"],
                            driver_data["name"],
                            driver_data["irating"],
                            driver_data["license_class"],
                            driver_data["license_level"],
                            driver_data["safety_rating"]
                        )
                    )
                    driver_id = cursor.fetchone()[0]
                
                self.conn.commit()
                return driver_id
        except Exception as e:
            logger.error(f"Error upserting driver profile: {e}")
            logger.error(f"Driver profile upsert error details: {traceback.format_exc()}")
            self.conn.rollback()
            raise
    
    def get_driver_id(self, iracing_id):
        """Get the driver ID from the iracing_id"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM driver_profile WHERE iracing_id = %s",
                    (iracing_id,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting driver ID: {e}")
            logger.error(f"Driver ID lookup error details: {traceback.format_exc()}")
            return None
    
    def insert_session(self, session_data):
        """Insert session information and return the session ID"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO sessions 
                    (iracing_session_id, session_type, track_id, start_time, end_time, 
                    weather_type, temp_track, temp_air)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        session_data["iracing_session_id"],
                        session_data["session_type"],
                        session_data["track_id"],
                        session_data["start_time"],
                        session_data["end_time"],
                        session_data["weather_type"],
                        session_data["temp_track"],
                        session_data["temp_air"]
                    )
                )
                session_id = cursor.fetchone()[0]
                self.conn.commit()
                return session_id
        except Exception as e:
            logger.error(f"Error inserting session: {e}")
            logger.error(f"Session insert error details: {traceback.format_exc()}")
            self.conn.rollback()
            raise
    
    def insert_lap(self, lap_data):
        """Insert lap information"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO laps 
                    (session_id, driver_id, car_id, lap_number, lap_time, sector1_time, 
                    sector2_time, sector3_time, fuel_used, incidents, valid_lap)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        lap_data["session_id"],
                        lap_data["driver_id"],
                        lap_data["car_id"],
                        lap_data["lap_number"],
                        lap_data["lap_time"],
                        lap_data.get("sector1_time"),
                        lap_data.get("sector2_time"),
                        lap_data.get("sector3_time"),
                        lap_data.get("fuel_used"),
                        lap_data.get("incidents", 0),
                        lap_data.get("valid_lap", True)
                    )
                )
                self.conn.commit()
        except Exception as e:
            logger.error(f"Error inserting lap: {e}")
            logger.error(f"Lap insert error details: {traceback.format_exc()}")
            self.conn.rollback()
            raise
    
    def insert_race_result(self, result_data):
        """Insert race result information"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO race_results 
                    (session_id, driver_id, car_id, starting_position, finishing_position, 
                    qualifying_time, average_lap, fastest_lap, laps_completed, laps_led, 
                    incidents, irating_change, safety_rating_change)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        result_data["session_id"],
                        result_data["driver_id"],
                        result_data["car_id"],
                        result_data["starting_position"],
                        result_data["finishing_position"],
                        result_data.get("qualifying_time"),
                        result_data.get("average_lap"),
                        result_data.get("fastest_lap"),
                        result_data["laps_completed"],
                        result_data.get("laps_led", 0),
                        result_data.get("incidents", 0),
                        result_data.get("irating_change"),
                        result_data.get("safety_rating_change")
                    )
                )
                self.conn.commit()
        except Exception as e:
            logger.error(f"Error inserting race result: {e}")
            logger.error(f"Race result insert error details: {traceback.format_exc()}")
            self.conn.rollback()
            raise
    
    def get_lap_times_by_track(self, track_id, limit=100):
        """Get lap times for a specific track"""
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT l.lap_time, t.name as track_name, t.config as track_config, 
                           c.name as car_name, s.session_type
                    FROM laps l
                    JOIN sessions s ON l.session_id = s.id
                    JOIN tracks t ON s.track_id = t.id
                    JOIN cars c ON l.car_id = c.id
                    WHERE t.id = %s AND l.valid_lap = TRUE
                    ORDER BY l.lap_time ASC
                    LIMIT %s
                    """,
                    (track_id, limit)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting lap times by track: {e}")
            logger.error(f"Lap times query error details: {traceback.format_exc()}")
            return []
    
    def get_recent_results(self, limit=10):
        """Get recent race results"""
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT r.finishing_position, r.starting_position, r.irating_change,
                           r.safety_rating_change, r.fastest_lap, r.laps_completed,
                           t.name as track_name, t.config as track_config,
                           s.session_type, s.start_time, c.name as car_name
                    FROM race_results r
                    JOIN sessions s ON r.session_id = s.id
                    JOIN tracks t ON s.track_id = t.id
                    JOIN cars c ON r.car_id = c.id
                    ORDER BY s.start_time DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting recent results: {e}")
            logger.error(f"Recent results query error details: {traceback.format_exc()}")
            return []