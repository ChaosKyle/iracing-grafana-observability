# Data Processing Flow

This document explains how data flows through the iRacing Grafana Observability system, from collection to visualization.

## Telemetry Data Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ iRacing     │    │ Python      │    │ Prometheus  │    │ Grafana     │
│ Telemetry   │───►│ Collector   │───►│ Metrics     │───►│ Dashboards  │
│ (.ibt files)│    │ (transform) │    │ (storage)   │    │ (visualize) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │
                          │ (Cloud Option)
                          ▼
                   ┌─────────────┐    ┌─────────────┐
                   │ Prometheus  │    │ Grafana     │
                   │ Remote      │───►│ Cloud       │
                   │ Write       │    │ Dashboards  │
                   └─────────────┘    └─────────────┘
```

## Race Results Data Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ iRacing     │    │ Python      │    │ PostgreSQL  │    │ Grafana     │
│ API         │───►│ Collector   │───►│ Database    │───►│ Dashboards  │
│ (race data) │    │ (transform) │    │ (storage)   │    │ (visualize) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                            │
                                            │ (Cloud Option)
                                            ▼
                                     ┌─────────────┐
                                     │ Grafana     │
                                     │ Cloud       │
                                     │ Dashboards  │
                                     └─────────────┘
```

## Data Processing Details

### Telemetry Data Processing

1. **Collection**:
   - iRacing generates `.ibt` telemetry files during racing sessions
   - These files contain high-frequency data about car performance (speed, throttle, brake, etc.)

2. **Transformation**:
   - Python collector loads and parses `.ibt` files
   - Data is converted to Prometheus metrics format
   - Metrics are exposed via HTTP endpoint on port 8000

3. **Storage**:
   - Prometheus scrapes the metrics endpoint every 15 seconds
   - Data is stored efficiently in Prometheus time-series database
   - For cloud deployments, metrics are remote_written to Grafana Cloud

4. **Visualization**:
   - Grafana queries Prometheus using PromQL
   - Dashboards display telemetry data in charts and graphs
   - Metrics can be analyzed in real-time or historically

### Race Results Processing

1. **Collection**:
   - Python collector authenticates with iRacing API
   - Retrieves race results, driver stats, and career information

2. **Transformation**:
   - Raw JSON data is processed and normalized
   - Relational data model is created for efficient storage

3. **Storage**:
   - Structured data is stored in PostgreSQL tables
   - Relationships between races, drivers, tracks maintained
   - Indexed for quick querying

4. **Visualization**:
   - Grafana connects to PostgreSQL using SQL
   - Dashboards show race history, driver progress, stats
   - Tables, graphs, and gauge displays used to visualize data

## Metrics Types

The following metrics types are used in Prometheus:

1. **Counters**: Cumulative metrics that only increase
   - Example: Total laps completed, distance traveled

2. **Gauges**: Metrics that can go up and down
   - Example: Current speed, RPM, throttle position

3. **Histograms**: Distribution of values
   - Example: Lap time distributions, braking point consistency

## Query Languages

- **PromQL**: Used for querying Prometheus time-series data
  - Examples: `rate(iracing_speed_mph[1m])`, `max_over_time(iracing_rpm[10m])`

- **SQL**: Used for querying PostgreSQL structured data
  - Examples: `SELECT AVG(position) FROM race_results WHERE driver_id = '12345'`