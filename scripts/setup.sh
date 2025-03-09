#!/bin/bash
# Setup script for local development environment

echo "Setting up iRacing Grafana Observability Project..."

# Detect OS
case "$(uname -s)" in
    Linux*)     OS=Linux;;
    Darwin*)    OS=Mac;;
    CYGWIN*)    OS=Windows;;
    MINGW*)     OS=Windows;;
    MSYS*)      OS=Windows;;
    *)          OS=Unknown;;
esac

echo "Detected OS: $OS"

# Check for required tools
check_command() {
    if command -v $1 >/dev/null 2>&1; then
        echo "✓ $1 is installed"
        return 0
    else
        echo "✗ $1 is required but not installed"
        return 1
    fi
}

# Check for Docker
if ! check_command docker; then
    echo "Please install Docker Desktop:"
    echo "  - Mac: https://docs.docker.com/desktop/install/mac-install/"
    echo "  - Windows: https://docs.docker.com/desktop/install/windows-install/"
    echo "  - Linux: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check for Docker Compose
if ! check_command docker-compose; then
    if ! docker compose version >/dev/null 2>&1; then
        echo "Please install Docker Compose:"
        echo "  It's typically included with Docker Desktop, or install separately."
        exit 1
    else
        echo "✓ Docker Compose plugin is installed"
    fi
fi

# Check for Python
PYTHON_CMD="python3"
if ! check_command $PYTHON_CMD; then
    PYTHON_CMD="python"
    if ! check_command $PYTHON_CMD; then
        echo "Please install Python 3:"
        echo "  - Mac: brew install python"
        echo "  - Windows: https://www.python.org/downloads/windows/"
        echo "  - Linux: apt install python3 (or your distro's package manager)"
        exit 1
    fi
fi

# Create virtual environment for Python if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
    
    # Activate the virtual environment
    if [ "$OS" = "Windows" ]; then
        # Use the appropriate activation for Git Bash/MINGW
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r python/requirements.txt
else
    echo "Python virtual environment already exists. Activating..."
    if [ "$OS" = "Windows" ]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
fi

# Check if environment file exists
if [ ! -f ".env" ]; then
    echo "Creating sample .env file from template..."
    if [ -f "docker/collector/config.env" ]; then
        cp docker/collector/config.env .env
    else
        cp .env.example .env
    fi
    echo "Please edit .env file with your credentials before continuing."
fi

# Check if port 3000 is already in use
check_port_3000() {
    echo "Checking if port 3000 is already in use..."
    if [ "$OS" = "Windows" ]; then
        # Check for port 3000 in use on Windows
        netstat -an | findstr ":3000" > /dev/null && return 0 || return 1
    else
        # For Mac and Linux, first check if netcat is available
        if command -v nc >/dev/null 2>&1; then
            nc -z localhost 3000 >/dev/null 2>&1 && return 0 || return 1
        else
            # Fallback to lsof if netcat is not available
            command -v lsof >/dev/null 2>&1 && lsof -i:3000 >/dev/null 2>&1 && return 0 || return 1
        fi
    fi
}

if check_port_3000; then
    echo "Port 3000 is already in use."
    
    # Find a different available port (starting from 3001)
    next_port=3001
    while [ "$next_port" -le 3020 ]; do
        if [ "$OS" = "Windows" ]; then
            netstat -an | findstr ":$next_port" > /dev/null || break
        else
            if command -v nc >/dev/null 2>&1; then
                nc -z localhost $next_port >/dev/null 2>&1 || break
            else
                command -v lsof >/dev/null 2>&1 && lsof -i:$next_port >/dev/null 2>&1 || break
            fi
        fi
        next_port=$((next_port + 1))
    done
    
    if [ "$next_port" -gt 3020 ]; then
        echo "Warning: Could not find an available port between 3001-3020."
        echo "Using port 3001 but it may conflict with existing services."
        next_port=3001
    fi
    
    echo "Configuring Grafana to use port $next_port instead of 3000"
    if grep -q "^GRAFANA_PORT=" .env; then
        # Update existing GRAFANA_PORT if it exists
        sed -i.bak "s/^GRAFANA_PORT=.*/GRAFANA_PORT=$next_port/" .env
    else
        # Add GRAFANA_PORT if it doesn't exist
        echo "GRAFANA_PORT=$next_port" >> .env
    fi
    echo "Grafana will be accessible at: http://localhost:$next_port"
else
    echo "Port 3000 is available for Grafana."
fi

# Create Docker volumes if they don't exist
echo "Creating Docker volumes if they don't exist..."
docker volume ls | grep -q "iracing-grafana-observability_postgres-data" || docker volume create iracing-grafana-observability_postgres-data
docker volume ls | grep -q "iracing-grafana-observability_influxdb-data" || docker volume create iracing-grafana-observability_influxdb-data

# Give instructions for next steps
echo
echo "Setup complete! Next steps:"
echo
echo "1. Edit .env file with your iRacing credentials and database passwords"
echo "2. Start the stack with: docker-compose up -d"
# Get the configured Grafana port from .env if available
if grep -q "^GRAFANA_PORT=" .env; then
    GRAFANA_PORT=$(grep "^GRAFANA_PORT=" .env | cut -d= -f2)
else
    GRAFANA_PORT=3000
fi
echo "3. Access Grafana at: http://localhost:$GRAFANA_PORT (default login: admin/admin)"
echo "4. To run the collector manually: python python/collectors/iracing_collector.py"
echo
echo "For more information, see the documentation in docs/ directory."

if [ "$OS" = "Windows" ]; then
    echo
    echo "Windows-specific notes:"
    echo "- If using PowerShell, use 'docker-compose' instead of 'docker compose'"
    echo "- Use 'venv\\Scripts\\activate' to activate the virtual environment"
    echo "- Use '\\' instead of '/' in file paths when not using Git Bash"
fi

if [ "$OS" = "Mac" ]; then
    echo
    echo "Mac-specific notes:"
    echo "- Check Docker Desktop resource settings if you experience performance issues"
    echo "- Ensure Docker has access to your iRacing directories if accessing local telemetry"
fi