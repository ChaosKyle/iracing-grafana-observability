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
import hashlib
import getpass
import webbrowser
import requests
import argparse
from datetime import datetime

def get_token(non_interactive=False, verbose=True, use_env=False):
    """Interactive process to get an iRacing auth token"""
    
    if verbose:
        print("iRacing Token Generator")
        print("=======================")
        print("This script will help you generate a token for the iRacing collector to use.")
        print("Due to CAPTCHA requirements, this process may need to be done manually.\n")
    
    # Get credentials
    if use_env:
        username = os.environ.get("IRACING_USERNAME")
        password = os.environ.get("IRACING_PASSWORD")
        
        if not username or not password:
            if verbose:
                print("Error: IRACING_USERNAME and IRACING_PASSWORD environment variables not set.")
            return False
        
        if verbose:
            print(f"Using credentials from environment variables for {username}")
    elif non_interactive:
        if verbose:
            print("Error: Non-interactive mode requires using environment variables.")
            print("Set IRACING_USERNAME and IRACING_PASSWORD or use --use-env flag.")
        return False
    else:
        username = input("iRacing Email: ")
        password = getpass.getpass("iRacing Password: ")
    
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
    
    # First try without CAPTCHA
    if verbose:
        print("\nAttempting authentication...")
    auth_url = "https://members-ng.iracing.com/auth"
    
    try:
        resp = session.post(auth_url, json=auth_data)
        if verbose:
            print(f"Status: {resp.status_code}")
        
        auth_resp = json.loads(resp.text)
        
        # Check if CAPTCHA is required
        if auth_resp.get("verificationRequired", False):
            if verbose:
                print("\nCAPTCHA verification required.")
            
            if non_interactive:
                # In non-interactive mode, we can't proceed with CAPTCHA verification
                if verbose:
                    print("Cannot proceed with CAPTCHA verification in non-interactive mode.")
                
                # Create a fallback token using credentials
                token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iracing_token.json")
                
                token_data = {
                    "type": "credentials",
                    "username": username,
                    "password": password,
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(token_file, "w") as f:
                    json.dump(token_data, f, indent=2)
                    
                if verbose:
                    print(f"\nFallback token saved to {token_file}")
                    print("This will require administrator to manually complete CAPTCHA verification.")
                
                return False
            
            # Interactive mode with CAPTCHA
            if verbose:
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
            
            if verbose:
                print(f"\nToken saved to {token_file}")
                print("\nThe collector will automatically use this token for authentication.")
                print("\nNOTE: This token typically expires after ~7 days. When you see authentication errors,")
                print("run this script again to generate a new token.")
            
            return True
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
                
                if verbose:
                    print(f"\nToken saved to {token_file}")
                    print("\nThe collector will automatically use this token for authentication.")
                    print("\nNOTE: This token typically expires after ~7 days. When you see authentication errors,")
                    print("run this script again to generate a new token.")
                
                return True
            else:
                if verbose:
                    print("\nFailed to get token directly. Check your credentials or try again later.")
                    print("Response:", resp.text)
                
                # Create a fallback token using credentials
                token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iracing_token.json")
                
                token_data = {
                    "type": "credentials",
                    "username": username,
                    "password": password,
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(token_file, "w") as f:
                    json.dump(token_data, f, indent=2)
                    
                if verbose:
                    print(f"\nFallback token saved to {token_file}")
                
                return False
    except Exception as e:
        if verbose:
            print(f"Error processing auth response: {e}")
            try:
                print("Response:", resp.text)
            except:
                pass
        
        # Create a fallback token using credentials
        token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iracing_token.json")
        
        token_data = {
            "type": "credentials",
            "username": username,
            "password": password,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(token_file, "w") as f:
            json.dump(token_data, f, indent=2)
            
        if verbose:
            print(f"\nFallback token saved to {token_file} due to error")
        
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an iRacing authentication token")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode (requires environment variables)")
    parser.add_argument("--quiet", action="store_true", help="Suppress output messages")
    parser.add_argument("--use-env", action="store_true", help="Use credentials from environment variables")
    args = parser.parse_args()
    
    success = get_token(
        non_interactive=args.non_interactive,
        verbose=not args.quiet,
        use_env=args.use_env or args.non_interactive
    )
    
    # In non-interactive mode, signal success/failure with exit code
    if args.non_interactive:
        sys.exit(0 if success else 1)