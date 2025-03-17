#!/bin/bash
# Script to refresh the iRacing authentication token

# Set the path for the token status check
TOKEN_FILE="/app/iracing_token.json"
TOKEN_STATUS_URL="http://localhost:8080/auth_status"

# Function to get the current token status
check_token_status() {
    echo "Checking token status..."
    if [ -f "$TOKEN_FILE" ]; then
        TOKEN_TYPE=$(grep -o '"type": *"[^"]*"' "$TOKEN_FILE" | cut -d'"' -f4)
        echo "Current token type: $TOKEN_TYPE"
        
        # Check if we can connect to the status endpoint
        if command -v curl &> /dev/null; then
            if curl -s "$TOKEN_STATUS_URL" | grep -q "authenticated.*true"; then
                echo "Token is valid"
                return 0
            else
                echo "Token is invalid or expired"
                return 1
            fi
        else
            # Fallback to file timestamp check if curl is not available
            TOKEN_AGE=$((($(date +%s) - $(date -r "$TOKEN_FILE" +%s)) / 86400))
            if [ "$TOKEN_AGE" -gt 6 ]; then
                echo "Token is older than 6 days and might be expired"
                return 1
            else
                echo "Token is less than 6 days old, assuming valid"
                return 0
            fi
        fi
    else
        echo "Token file does not exist"
        return 1
    fi
}

# Function to generate a new token using credentials authentication
generate_token_from_env() {
    echo "Generating token using environment variables..."
    
    # Create a temporary Python script to generate the token
    cat > /tmp/generate_token.py << 'EOL'
#!/usr/bin/env python3
import os
import json
import base64
import hashlib
import requests
from datetime import datetime

# Get credentials from environment
username = os.getenv("IRACING_USERNAME")
password = os.getenv("IRACING_PASSWORD")

if not username or not password:
    print("ERROR: IRACING_USERNAME and IRACING_PASSWORD environment variables must be set")
    exit(1)

# Create session with proper headers
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
})

# Prepare login data
email_lower = username.lower()
hash_input = f"{password}{email_lower}"
hash_bytes = hashlib.sha256(hash_input.encode('utf-8')).digest()
encoded_password = base64.b64encode(hash_bytes).decode('utf-8')

# Prepare the authentication JSON payload
auth_data = {
    "email": username,
    "password": encoded_password
}

# Try authentication
print("Attempting authentication...")
auth_url = "https://members-ng.iracing.com/auth"

try:
    resp = session.post(auth_url, json=auth_data)
    print(f"Status: {resp.status_code}")
    
    auth_resp = json.loads(resp.text)
    
    # Check if CAPTCHA is required
    if auth_resp.get("verificationRequired", False):
        print("CAPTCHA verification required. Cannot proceed with automated authentication.")
        print("Using fallback token method...")
        
        # Create a fallback credentials token
        token_data = {
            "type": "credentials",
            "username": username,
            "password": password,
            "timestamp": datetime.now().isoformat()
        }
        
        with open("/app/iracing_token.json", "w") as f:
            json.dump(token_data, f, indent=2)
            
        print("Fallback token saved. This will trigger the manual token flow during collection.")
        
    else:
        # Check if we got a direct token
        if "authcode" in auth_resp and auth_resp["authcode"] != 0:
            token = auth_resp["authcode"]
            
            # Save the token to a file
            token_data = {
                "type": "bearer",
                "value": token,
                "timestamp": datetime.now().isoformat(),
                "username": username
            }
            
            with open("/app/iracing_token.json", "w") as f:
                json.dump(token_data, f, indent=2)
            
            print("Bearer token saved successfully.")
        else:
            print("Failed to get token directly.")
            print("Response:", resp.text)
            
            # Create a fallback credentials token
            token_data = {
                "type": "credentials",
                "username": username,
                "password": password,
                "timestamp": datetime.now().isoformat()
            }
            
            with open("/app/iracing_token.json", "w") as f:
                json.dump(token_data, f, indent=2)
                
            print("Fallback token saved. This will trigger the manual token flow during collection.")
except Exception as e:
    print(f"Error processing auth response: {e}")
    
    # Create a fallback credentials token
    token_data = {
        "type": "credentials",
        "username": username,
        "password": password,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("/app/iracing_token.json", "w") as f:
        json.dump(token_data, f, indent=2)
        
    print("Fallback token saved due to error.")
EOL

    # Execute the token generation script
    python3 /tmp/generate_token.py
    rm /tmp/generate_token.py
}

# Check if we need a new token
if ! check_token_status; then
    generate_token_from_env
    echo "Token refresh complete"
else
    echo "Token is still valid, no refresh needed"
fi

exit 0