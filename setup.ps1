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
Write-Host "3. Access Grafana at: http://localhost:3000 (default login: admin/admin)"
Write-Host "4. To run the collector manually: python python\collectors\iracing_collector.py"
Write-Host
Write-Host "Windows-specific notes:" -ForegroundColor Yellow
Write-Host "- In PowerShell, you may need to use 'docker-compose' instead of 'docker compose'"
Write-Host "- Use '.\venv\Scripts\Activate.ps1' to activate the virtual environment in PowerShell"
Write-Host "- Ensure Docker Desktop has WSL 2 backend enabled for best performance"
Write-Host "- Check Windows Firewall settings if you have connectivity issues"
Write-Host
Write-Host "For more information, see the documentation in docs\ directory."