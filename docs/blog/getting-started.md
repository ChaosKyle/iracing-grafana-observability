# Getting Started with iRacing Telemetry Visualization

*Updated: March 15, 2025*

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
git clone https://github.com/ChaosKyle/iracing-grafana-observability.git
cd iracing-grafana-observability
```

2. **Configure your credentials**:

Create a `.env` file in the project root with your iRacing credentials:

```
# iRacing Credentials
IRACING_USERNAME=your_iracing_username
IRACING_PASSWORD=your_iracing_password
IRACING_CUSTOMER_ID=your_customer_id  # Optional but recommended

# Authentication Strategy
AUTH_STRATEGY=token_file  # Recommended for handling CAPTCHA

# Database Credentials (can leave as defaults for local setup)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=iracing_data

# Prometheus Configuration (can leave as defaults for local setup)
PROMETHEUS_HOST=prometheus
PROMETHEUS_PORT=9090
```

3. **Generate Authentication Token** (required for CAPTCHA bypass):

Since March 2025, iRacing requires CAPTCHA verification during login. You'll need to generate a token to bypass this:

```bash
# Make the script executable
chmod +x scripts/generate-token.sh

# Run the token generator
./scripts/generate-token.sh
```

Follow the prompts in the script:
- Enter your iRacing credentials
- If CAPTCHA is required, the script will open a browser window
- Log in manually to iRacing through the browser
- Copy the authentication cookie as instructed
- Paste it back into the terminal

This token will be valid for approximately 7 days.

4. **Start the stack**:

```bash
docker-compose up -d
```

This command starts PostgreSQL, Prometheus, Grafana, and the data collector in the background.

5. **Access your dashboards**:

- **Grafana**: Open http://localhost:3000 in your browser. Log in with the default credentials (admin/admin), and you'll see the pre-configured dashboards ready to use.
- **Collector Dashboard**: Visit http://localhost:8080 to monitor authentication status and generate new tokens when needed.

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

1. **Historical data**: The collector automatically fetches your historical race results when it first runs. It will collect:
   - Your recent race results
   - Career statistics
   - Safety rating and iRating history

2. **Telemetry data**: For telemetry visualization, you'll need to configure your iRacing client to save telemetry files:
   - In the iRacing UI, go to Options > Telemetry and set "Disk telemetry" to "On"
   - Set the telemetry directory path in your `.env` file: `RACELABS_TELEMETRY_DIR=/path/to/telemetry`
   - For Windows, use format like `RACELABS_TELEMETRY_DIR=C:/Users/Username/Documents/iRacing/telemetry`

3. **Manual collection**: If you want to trigger data collection manually, run:

```bash
docker-compose restart collector
```

4. **Monitor collection status**:
   - Visit the collector dashboard at http://localhost:8080
   - Check "Collection Statistics" section for the latest data
   - Review authentication status to ensure the token is valid

## Customizing Your Experience

Once you're familiar with the basic setup, you can customize the platform to better suit your needs:

- **Create custom dashboards**: Use Grafana's built-in editor to create dashboards that focus on aspects you care about most.
- **Add teammates**: Share your installation with teammates to compare data and learn from each other.
- **Extend with plugins**: Add Grafana plugins for additional visualization types or data sources.

## Troubleshooting

### Authentication Issues

If you encounter authentication problems:

1. **Token Expiration**: Tokens typically last 7 days. When expired:
   - Visit http://localhost:8080 and click "Generate New Token"
   - Or run `./scripts/generate-token.sh` again
   
2. **CAPTCHA Errors**: If you see "Authentication requires CAPTCHA verification" errors:
   - Check the authentication status on the collector dashboard
   - Generate a new token following the guided process
   - Ensure you're copying the correct cookie value (`irsso_membersv2`)

3. **Connection Issues**:
   - Verify your network can reach the iRacing servers
   - Check Docker container connectivity with `docker-compose ps`
   - Review logs with `docker-compose logs collector`

### Data Collection Issues

If no data appears in Grafana:

1. **Database Connection**: Ensure the collector can connect to PostgreSQL and Prometheus:
   ```bash
   docker-compose logs collector | grep database
   ```

2. **iRacing API Access**: Check if your credentials are correct and API limits:
   ```bash
   # View recent authentication attempts
   docker-compose logs collector | grep auth
   ```

3. **Telemetry Files**: Verify telemetry files are being saved to the correct location and are accessible to the collector

## Token Renewal Process

Authentication tokens need to be renewed approximately every 7 days:

1. **Check Token Status**: Visit http://localhost:8080 to see when your token expires
2. **Generate New Token**: Run the token generator a day before expiration:
   ```bash
   ./scripts/generate-token.sh
   ```
3. **Set Calendar Reminder**: Add a calendar reminder every 6 days to check your token status

## Conclusion

With the iRacing Grafana Observability Project, you now have a powerful platform for analyzing your sim racing performance. The combination of historical race data and detailed telemetry visualizations provides insights that were previously only available to professional racing teams.

The improved authentication system ensures you can maintain reliable access to your data even with iRacing's CAPTCHA requirements. As you use this tool, you'll develop a better understanding of your driving style, identify specific areas for improvement, and ultimately become a more competitive sim racer.

Happy racing, and may your lap times continuously improve!