#!/bin/bash
# Script to generate an iRacing authentication token for the collector

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TOKEN_SCRIPT="$PROJECT_ROOT/python/get_iracing_token.py"

echo "iRacing Authentication Token Generator"
echo "====================================="

# Ensure Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Check if using Windows with Git Bash
if [[ "$OSTYPE" == "msys" ]]; then
    echo "Detected Windows with Git Bash..."
    echo "For best results on Windows, use PowerShell or CMD and run: python $TOKEN_SCRIPT"
    
    read -p "Continue anyway? (y/n): " CONT
    if [[ "$CONT" != "y" ]]; then
        exit 0
    fi
fi

# Check if we're in a Docker container
if [ -f /.dockerenv ]; then
    IN_DOCKER=true
    echo "Running inside Docker container"
else
    IN_DOCKER=false
fi

# Check if we have proper credentials in environment
if [ -z "$IRACING_USERNAME" ] || [ -z "$IRACING_PASSWORD" ]; then
    echo "No credentials found in environment variables."
    echo "You'll be prompted to enter them interactively."
    
    # For non-Docker environments, run the Python script directly
    if [ "$IN_DOCKER" = false ]; then
        python3 "$TOKEN_SCRIPT"
        exit $?
    fi
fi

# Handle Docker-specific case
if [ "$IN_DOCKER" = true ]; then
    echo "Using credentials from environment variables"
    
    # Generate token using environment credentials
    echo "Running token generation script..."
    python3 "$TOKEN_SCRIPT" --non-interactive
    
    STATUS=$?
    if [ $STATUS -ne 0 ]; then
        echo "Token generation failed with status $STATUS"
        echo "This likely means CAPTCHA verification is required."
        echo "Please run the script on your host machine to complete verification."
        exit $STATUS
    fi
    
    echo "Token generation complete"
    exit 0
fi

# For non-Docker: run the Python script directly
python3 "$TOKEN_SCRIPT"