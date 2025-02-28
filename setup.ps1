# PowerShell setup script for Windows

Write-Host "Setting up iRacing Grafana Observability Project..." -ForegroundColor Green

# Function to check if a command exists
function Test-CommandExists {
    param ($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    if ($exists) {
        Write-Host "✓ $command is installed" -ForegroundColor Green
    }
    else {
        Write-Host "✗ $command is required but not installed" -ForegroundColor Red
    }
    return $exists
}

# Check for Docker
if (-not (Test-CommandExists "docker")) {
    Write-Host "Please install Docker Desktop for Windows:"
    Write-Host "  https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

# Check for Docker Compose
$dockerComposeExists = Test-CommandExists "docker-compose"
if (-not $dockerComposeExists) {
    # Try the Docker Compose plugin
    try {
        $null = docker compose version
        Write-Host "✓ Docker Compose plugin is installed" -ForegroundColor Green
    }
    catch {
        Write-Host "Please install Docker Compose (should be included with Docker Desktop)" -ForegroundColor Red
        exit 1
    }
}

# Check for Python
$pythonCmd = "python"
if (-not (Test-CommandExists $pythonCmd)) {
    Write-Host "Please install Python 3 from https://www.python.org/downloads/windows/" -ForegroundColor Red
    exit 1
}

# Verify Python version is 3.x
$pythonVersion = & $pythonCmd --version
if (-not $pythonVersion.Contains("Python 3")) {
    Write-Host "Python 3.x is required. You have: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Create virtual environment for Python if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    & $pythonCmd -m venv venv
    
    # Activate the virtual environment
    & .\venv\Scripts\Activate.ps1
    
    # Install dependencies
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    & pip install --upgrade pip
    & pip install -r python\requirements.txt
}
else {
    Write-Host "Python virtual environment already exists. Activating..." -ForegroundColor Cyan
    & .\venv\Scripts\Activate.ps1
}

# Check if environment file exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating sample .env file from template..." -ForegroundColor Cyan
    if (Test-Path "docker\collector\config.env") {
        Copy-Item "docker\collector\config.env" -Destination ".env"
    }
    elseif (Test-Path ".env.example") {
        Copy-Item ".env.example" -Destination ".env"
    }
    Write-Host "Please edit .env file with your credentials before continuing." -ForegroundColor Yellow
}

# Check if port 3000 is already in use
Write-Host "Checking if Grafana port 3000 is already in use..." -ForegroundColor Cyan
$port3000InUse = $null -ne (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue)

if ($port3000InUse) {
    Write-Host "Port 3000 is already in use." -ForegroundColor Yellow
    
    # Find a different available port (starting from 3001)
    $nextPort = 3001
    while ($nextPort -le 3020) {
        $portInUse = $null -ne (Get-NetTCPConnection -LocalPort $nextPort -ErrorAction SilentlyContinue)
        if (-not $portInUse) {
            break
        }
        $nextPort++
    }
    
    if ($nextPort -gt 3020) {
        Write-Host "Warning: Could not find an available port between 3001-3020." -ForegroundColor Yellow
        Write-Host "Using port 3001 but it may conflict with existing services." -ForegroundColor Yellow
        $nextPort = 3001
    }
    
    Write-Host "Configuring Grafana to use port $nextPort instead of 3000" -ForegroundColor Green
    
    # Check if GRAFANA_PORT already exists in .env
    $envContent = Get-Content ".env"
    $grafanaPortExists = $envContent | Where-Object { $_ -match "^GRAFANA_PORT=" }
    
    if ($grafanaPortExists) {
        # Update existing GRAFANA_PORT
        $updatedContent = $envContent -replace "^GRAFANA_PORT=.*", "GRAFANA_PORT=$nextPort"
        Set-Content -Path ".env" -Value $updatedContent
    } else {
        # Add GRAFANA_PORT if it doesn't exist
        Add-Content -Path ".env" -Value "GRAFANA_PORT=$nextPort"
    }
    
    Write-Host "Grafana will be accessible at: http://localhost:$nextPort" -ForegroundColor Green
} else {
    Write-Host "Port 3000 is available for Grafana." -ForegroundColor Green
}

# Create Docker volumes if they don't exist
Write-Host "Creating Docker volumes if they don't exist..." -ForegroundColor Cyan
$postgresVolumeExists = docker volume ls | Select-String "iracing-grafana-observability_postgres-data"
if (-not $postgresVolumeExists) {
    docker volume create iracing-grafana-observability_postgres-data
}

$influxVolumeExists = docker volume ls | Select-String "iracing-grafana-observability_influxdb-data"
if (-not $influxVolumeExists) {
    docker volume create iracing-grafana-observability_influxdb-data
}

# Give instructions for next steps
Write-Host "`nSetup complete! Next steps:" -ForegroundColor Green
Write-Host
Write-Host "1. Edit .env file with your iRacing credentials and database passwords"
Write-Host "2. Start the stack with: docker-compose up -d"
# Get configured Grafana port
$grafanaPort = "3000"
if (Test-Path ".env") {
    $portMatch = Get-Content ".env" | Select-String "^GRAFANA_PORT=(\d+)"
    if ($portMatch) {
        $grafanaPort = $portMatch.Matches.Groups[1].Value
    }
}
Write-Host "3. Access Grafana at: http://localhost:$grafanaPort (default login: admin/admin)"
Write-Host "4. To run the collector manually: python python\collectors\iracing_collector.py"
Write-Host
Write-Host "Windows-specific notes:" -ForegroundColor Yellow
Write-Host "- In PowerShell, you may need to use 'docker-compose' instead of 'docker compose'"
Write-Host "- Use '.\venv\Scripts\Activate.ps1' to activate the virtual environment in PowerShell"
Write-Host "- Ensure Docker Desktop has WSL 2 backend enabled for best performance"
Write-Host "- Check Windows Firewall settings if you have connectivity issues"
Write-Host
Write-Host "For more information, see the documentation in docs\ directory."