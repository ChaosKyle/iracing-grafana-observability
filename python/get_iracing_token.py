#!/usr/bin/env python3
"""
Script to manually get an iRacing authentication token and store it for the collector

Since the iRacing API now requires CAPTCHA verification, we need a way to manually
authenticate and save the token for the collector to use.
"""

import os
import sys
import json
import base64
import getpass
import webbrowser
import requests
from datetime import datetime

def get_token():
    """Interactive process to get an iRacing auth token"""
    
    print("iRacing Token Generator")
    print("=======================")
    print("This script will help you generate a token for the iRacing collector to use.")
    print("Due to CAPTCHA requirements, this process needs to be done manually.\n")
    
    # Get credentials
    username = input("iRacing Email: ")
    password = getpass.getpass("iRacing Password: ")
    
    # Create session with proper headers
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    
    # Base64 encode the password
    password_hash = base64.b64encode(password.encode('utf-8')).decode('utf-8')
    
    # Prepare login data
    auth_data = {
        "email": username,
        "password": password_hash
    }
    
    # First try without CAPTCHA
    print("\nAttempting authentication...")
    auth_url = "https://members-ng.iracing.com/auth"
    
    resp = session.post(auth_url, json=auth_data)
    print(f"Status: {resp.status_code}")
    
    try:
        auth_resp = json.loads(resp.text)
        
        # Check if CAPTCHA is required
        if auth_resp.get("verificationRequired", False):
            print("\nCAPTCHA verification required.")
            print("Opening iRacing website for manual login...")
            
            # Open web browser for manual login
            webbrowser.open("https://members.iracing.com/membersite/login.jsp")
            
            print("\nPlease log in manually in the browser window that opened.")
            print("Once logged in, copy your irsso_membersv2 cookie value.")
            print("You can find this in your browser's developer tools under Application -> Storage -> Cookies.")
            print("Look for the cookie named 'irsso_membersv2'.\n")
            
            cookie_value = input("Enter irsso_membersv2 cookie value: ")
            
            # Save the cookie value to a file
            token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iracing_token.json")
            
            token_data = {
                "type": "cookie",
                "name": "irsso_membersv2",
                "value": cookie_value,
                "timestamp": datetime.now().isoformat(),
                "username": username
            }
            
            with open(token_file, "w") as f:
                json.dump(token_data, f, indent=2)
            
            print(f"\nToken saved to {token_file}")
            print("\nUpdate the collector to use this token file.")
        else:
            # Check if we got a direct token
            if "authcode" in auth_resp and auth_resp["authcode"] != 0:
                token = auth_resp["authcode"]
                
                # Save the token to a file
                token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iracing_token.json")
                
                token_data = {
                    "type": "bearer",
                    "value": token,
                    "timestamp": datetime.now().isoformat(),
                    "username": username
                }
                
                with open(token_file, "w") as f:
                    json.dump(token_data, f, indent=2)
                
                print(f"\nToken saved to {token_file}")
                print("\nUpdate the collector to use this token file.")
            else:
                print("\nFailed to get token directly.")
                print("Response:", resp.text)
    except Exception as e:
        print(f"Error processing auth response: {e}")
        print("Response:", resp.text)

if __name__ == "__main__":
    get_token()