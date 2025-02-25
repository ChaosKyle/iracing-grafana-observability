-- iRacing database schema

-- Tracks table
CREATE TABLE IF NOT EXISTS tracks (
    id SERIAL PRIMARY KEY,
    iracing_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    config VARCHAR(255),
    length_km DECIMAL(10, 3),
    corners INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cars table
CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    iracing_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    class VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Driver profile table
CREATE TABLE IF NOT EXISTS driver_profile (
    id SERIAL PRIMARY KEY,
    iracing_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    irating INTEGER,
    license_class VARCHAR(10),
    license_level DECIMAL(3,2),
    safety_rating DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    iracing_session_id BIGINT UNIQUE NOT NULL,
    session_type VARCHAR(50) NOT NULL, -- Race, Practice, Qualify, etc.
    track_id INTEGER REFERENCES tracks(id),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    weather_type VARCHAR(50),
    temp_track DECIMAL(5,2),
    temp_air DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Laps table
CREATE TABLE IF NOT EXISTS laps (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    driver_id INTEGER REFERENCES driver_profile(id),
    car_id INTEGER REFERENCES cars(id),
    lap_number INTEGER NOT NULL,
    lap_time DECIMAL(10, 3), -- in seconds
    sector1_time DECIMAL(10, 3),
    sector2_time DECIMAL(10, 3),
    sector3_time DECIMAL(10, 3),
    fuel_used DECIMAL(10, 3),
    incidents INTEGER DEFAULT 0,
    valid_lap BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Race results table
CREATE TABLE IF NOT EXISTS race_results (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    driver_id INTEGER REFERENCES driver_profile(id),
    car_id INTEGER REFERENCES cars(id),
    starting_position INTEGER,
    finishing_position INTEGER,
    qualifying_time DECIMAL(10, 3),
    average_lap DECIMAL(10, 3),
    fastest_lap DECIMAL(10, 3),
    laps_completed INTEGER,
    laps_led INTEGER,
    incidents INTEGER,
    irating_change INTEGER,
    safety_rating_change DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_laps_session_id ON laps(session_id);
CREATE INDEX IF NOT EXISTS idx_laps_driver_id ON laps(driver_id);
CREATE INDEX IF NOT EXISTS idx_race_results_session_id ON race_results(session_id);
CREATE INDEX IF NOT EXISTS idx_race_results_driver_id ON race_results(driver_id);
