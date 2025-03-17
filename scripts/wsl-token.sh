#!/bin/bash
# Helper script for generating iRacing tokens in WSL environment

# Navigate to the python directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/../python"

# Display instructions
echo "===== iRacing Token Generator for WSL ====="
echo "This helper script will guide you through generating an authentication token"
echo "when running in Windows Subsystem for Linux (WSL)."
echo
echo "Options:"
echo "  1. Try automatic browser opening (uses Windows browser)"
echo "  2. Manual mode (just show URL to visit in any browser)"
echo
read -p "Enter your choice (1/2): " choice

if [ "$choice" = "1" ]; then
  echo "Attempting to open browser automatically..."
  python3 get_iracing_token.py
elif [ "$choice" = "2" ]; then
  echo "Using manual URL mode..."
  python3 get_iracing_token.py --manual-url
else
  echo "Invalid choice. Exiting."
  exit 1
fi

echo
echo "If token generation was successful, the collector should now be able to authenticate with iRacing."
echo "The token is stored in: $(pwd)/iracing_token.json"