# Getting Started with iRacing Telemetry Visualization

*Date: February 25, 2025*

Sim racing has evolved from a simple hobby into a sophisticated pursuit where data analysis can provide a competitive edge. If you're an iRacing enthusiast looking to improve your performance through data-driven insights, this guide will help you set up a comprehensive telemetry visualization solution using the iRacing Grafana Observability Project.

## Why Analyze Your Telemetry Data?

Before diving into the technical setup, let's consider why telemetry analysis is worth your time:

1. **Identify Braking Points**: See exactly where the fastest drivers brake and how they modulate brake pressure
2. **Optimize Racing Lines**: Compare your racing line against your fastest laps or those of others
3. **Refine Setup Choices**: Understand how setup changes affect car behavior in specific corners
4. **Develop Consistency**: Track your performance across multiple sessions to identify areas for improvement
5. **Plan Race Strategy**: Analyze fuel consumption and tire wear to optimize pit strategies

## Setting Up Your Environment

The iRacing Grafana Observability Project brings together several powerful open-source technologies to create a comprehensive telemetry visualization platform. Here's how to get started:

### Prerequisites

Before you begin, ensure you have:

- An active iRacing subscription
- Docker and Docker Compose installed on your system
- Basic familiarity with command-line interfaces
- About 2GB of free disk space

### Installation

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/iracing-grafana-observability.git
cd iracing-grafana-observability
```

2. **Configure your credentials**:

Create a `.env` file in the project root with your iRacing credentials:

```
IRACING_USERNAME=your_iracing_username
IRACING_PASSWORD=your_iracing_password
POSTGRES_PASSWORD=secure_password
INFLUXDB_ADMIN_PASSWORD=secure_password
```

3. **Start the stack**:

```bash
docker-compose up -d
```

This command starts PostgreSQL, InfluxDB, Grafana, and the data collector in the background.

4. **Access your dashboards**:

Open your browser and navigate to `http://localhost:3000`. Log in with the default credentials (admin/admin), and you'll see the pre-configured dashboards ready to use.

## Exploring The Dashboards

The project includes several dashboards designed to give you insights into different aspects of your racing performance:

### 1. Performance Analysis

This dashboard shows your iRating and Safety Rating trends over time, along with statistics about your race finishes, qualifying positions, and incidents per race.

### 2. Telemetry Visualization

Dive deep into your driving technique with visualizations of throttle, brake, steering inputs, and resulting car behavior like speed, RPM, and lateral G-forces.

### 3. Race Strategy

Analyze your fuel consumption, lap time consistency, and pit stop efficiency to optimize your race strategy.

### 4. Track Insights

Compare your performance across different tracks and corners to identify your strengths and weaknesses.

## Collecting Your First Data

After setting up the environment, you'll need to collect some data to populate your dashboards:

1. **Historical data**: The collector automatically fetches your historical race results when it first runs.

2. **Telemetry data**: For telemetry visualization, you'll need to configure your iRacing client to save telemetry files. In the iRacing UI, go to Options > Telemetry and set "Disk telemetry" to "On".

3. **Manual collection**: If you want to trigger data collection manually, run:

```bash
docker-compose exec collector python collectors/iracing_collector.py
```

## Customizing Your Experience

Once you're familiar with the basic setup, you can customize the platform to better suit your needs:

- **Create custom dashboards**: Use Grafana's built-in editor to create dashboards that focus on aspects you care about most.
- **Add teammates**: Share your installation with teammates to compare data and learn from each other.
- **Extend with plugins**: Add Grafana plugins for additional visualization types or data sources.

## Conclusion

With the iRacing Grafana Observability Project, you now have a powerful platform for analyzing your sim racing performance. The combination of historical race data and detailed telemetry visualizations provides insights that were previously only available to professional racing teams.

As you use this tool, you'll develop a better understanding of your driving style, identify specific areas for improvement, and ultimately become a more competitive sim racer.

Happy racing, and may your lap times continuously improve!