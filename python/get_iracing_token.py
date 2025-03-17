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
import subprocess
import platform
from datetime import datetime

def open_browser_url(url, verbose=True):
    """
    Try multiple methods to open a URL, optimized for WSL environments
    where standard browser opening may fail.
    
    Returns True if a method succeeded, False otherwise.
    """
    # Method 1: Try standard webbrowser module
    try:
        if verbose:
            print("Attempting to open browser with standard method...")
        webbrowser.open(url)
        if verbose:
            print("Browser should be opening now.")
        return True
    except Exception as e:
        if verbose:
            print(f"Standard browser open failed: {e}")
    
    # Method 2: For WSL, try using cmd.exe to open in Windows browser
    if "microsoft" in platform.uname().release.lower() or "wsl" in platform.uname().release.lower():
        try:
            if verbose:
                print("Detected WSL environment, trying Windows browser...")
            cmd = ['cmd.exe', '/c', f'start {url}']
            subprocess.run(cmd, check=True)
            if verbose:
                print("Windows browser should be opening now.")
            return True
        except Exception as e:
            if verbose:
                print(f"Windows browser open failed: {e}")
    
    # Method 3: If on Linux, try common browsers directly
    browsers = ['google-chrome', 'chrome', 'firefox', 'brave-browser', 'chromium']
    for browser in browsers:
        try:
            if verbose:
                print(f"Trying to open with {browser}...")
            subprocess.run([browser, url], check=True)
            if verbose:
                print(f"Browser {browser} should be opening now.")
            return True
        except:
            pass
    
    # If we got here, all methods failed
    if verbose:
        print("\nUnable to automatically open a browser.")
        print(f"Please manually navigate to: {url}")
        print("After logging in, copy the irsso_membersv2 cookie value.")
    
    return False

def get_token(non_interactive=False, verbose=True, use_env=False, manual_url=False):
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
            login_url = "https://members.iracing.com/membersite/login.jsp"
            
            if verbose:
                print("Manual login required for CAPTCHA verification.")
                
                if not manual_url:
                    print("Attempting to open iRacing website for manual login...")
                    browser_opened = open_browser_url(login_url, verbose)
                else:
                    browser_opened = False
                
                print("\nPlease log in to iRacing at:")
                print(f"{login_url}")
                print("\nOnce logged in, copy your irsso_membersv2 cookie value.")
                print("You can find this in your browser's developer tools:")
                print("1. Right-click anywhere on the page and select 'Inspect' or press F12")
                print("2. Go to the 'Application' tab in Chrome (or 'Storage' in Firefox)")
                print("3. Expand 'Cookies' in the left panel and select 'https://members.iracing.com'")
                print("4. Find the cookie named 'irsso_membersv2' and copy its value")
                print("\nNote: The cookie is usually a long string starting with 'IRMC_...'")
            
            cookie_value = input("\nEnter irsso_membersv2 cookie value: ")
            
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
    parser.add_argument("--manual-url", action="store_true", help="Skip browser opening attempt, just show the URL to visit")
    args = parser.parse_args()
    
    success = get_token(
        non_interactive=args.non_interactive,
        verbose=not args.quiet,
        use_env=args.use_env or args.non_interactive,
        manual_url=args.manual_url
    )
    
    # In non-interactive mode, signal success/failure with exit code
    if args.non_interactive:
        sys.exit(0 if success else 1)