#!/usr/bin/env python3

"""
Script to update the collector container's authentication strategy.

This script will create a modified authentication file and restart the collector.
"""

import os
import json
import sys
import base64
import hashlib
import hmac
import subprocess

def main():
    print("iRacing Authentication Strategy Update")
    print("=====================================")
    print("This script will update the authentication approach to help with CAPTCHA issues.")
    
    # Check if we already have a token file
    token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iracing_token.json")
    
    if os.path.exists(token_file):
        print(f"\nFound existing token file at {token_file}")
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
                print(f"Token type: {token_data.get('type', 'unknown')}")
        except Exception as e:
            print(f"Error reading token file: {e}")
    
    # Get credentials
    username = input("\nEnter your iRacing email: ")
    password = input("Enter your iRacing password: ")
    
    # Create a token file with direct credentials
    token_data = {
        "type": "credentials",
        "username": username,
        "password": password,
        "timestamp": "2025-03-09T20:00:00.000Z"
    }
    
    # Save the token file
    with open(token_file, 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print(f"\nSaved credentials to {token_file}")
    
    # Check if running in Docker
    try:
        subprocess.run(["docker", "ps"], capture_output=True, check=True)
        in_docker = True
    except:
        in_docker = False
    
    if in_docker:
        print("\nDetected Docker environment. Would you like to restart the collector container? (y/n)")
        restart = input().lower().strip()
        
        if restart == 'y':
            try:
                subprocess.run(["docker-compose", "restart", "collector"], check=True)
                print("\nCollector container restarted successfully!")
            except Exception as e:
                print(f"\nError restarting collector container: {e}")
                print("Please restart the collector manually with: docker-compose restart collector")
    
    print("\nAuthentication strategy updated!")
    print("\nNotes:")
    print("1. The collector will now use these credentials directly to authenticate")
    print("2. If you're still seeing authentication errors, check for rate limiting (429 errors)")
    print("3. You may need to wait a few minutes if you've been rate limited")

if __name__ == "__main__":
    main()