#!/usr/bin/env python3
"""
Authentication Strategy Module for iRacing API

This module provides different authentication strategies for the iRacing API,
allowing for flexible token handling depending on deployment environment.
"""

import os
import json
import base64
import hashlib
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger("auth_strategy")

class AuthStrategy:
    """Base class for authentication strategies"""
    
    def get_token_data(self):
        """Get the authentication token data"""
        raise NotImplementedError("Subclasses must implement get_token_data")
    
    def refresh_token(self):
        """Refresh the authentication token"""
        raise NotImplementedError("Subclasses must implement refresh_token")
    
    def get_auth_status(self):
        """Get the authentication status"""
        raise NotImplementedError("Subclasses must implement get_auth_status")

class DirectApiStrategy(AuthStrategy):
    """Direct API authentication using username/password"""
    
    def __init__(self, username=None, password=None):
        self.username = username or os.getenv("IRACING_USERNAME")
        self.password = password or os.getenv("IRACING_PASSWORD")
        self.last_auth_time = None
        self.auth_token = None
        
        if not self.username or not self.password:
            raise ValueError("Username and password are required for DirectApiStrategy")
    
    def get_token_data(self):
        """Get token data by direct API authentication"""
        if self.auth_token and self.last_auth_time:
            # Check if token is still valid (less than 6 hours old)
            if datetime.now() - self.last_auth_time < timedelta(hours=6):
                return {"type": "bearer", "value": self.auth_token}
        
        # Need to authenticate
        auth_data = self._authenticate()
        if auth_data and auth_data.get("type") == "bearer":
            self.auth_token = auth_data.get("value")
            self.last_auth_time = datetime.now()
        
        return auth_data
    
    def _authenticate(self):
        """Authenticate with iRacing API directly"""
        try:
            # Create session with proper headers
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json"
            })
            
            # Prepare login data
            email_lower = self.username.lower()
            hash_input = f"{self.password}{email_lower}"
            hash_bytes = hashlib.sha256(hash_input.encode('utf-8')).digest()
            encoded_password = base64.b64encode(hash_bytes).decode('utf-8')
            
            # Prepare the authentication JSON payload
            auth_data = {
                "email": self.username,
                "password": encoded_password
            }
            
            # Make the authentication request
            resp = session.post("https://members-ng.iracing.com/auth", json=auth_data)
            
            if resp.status_code == 200:
                try:
                    auth_resp = resp.json()
                    
                    # Check if CAPTCHA is required
                    if auth_resp.get("verificationRequired", False):
                        logger.error("Authentication requires CAPTCHA verification. Cannot proceed with automated authentication.")
                        # Return credential-based token as fallback
                        return {
                            "type": "credentials", 
                            "username": self.username, 
                            "password": self.password
                        }
                    
                    # Check for auth token
                    if "authcode" in auth_resp and auth_resp["authcode"] != 0:
                        return {"type": "bearer", "value": auth_resp["authcode"]}
                    
                    logger.error(f"Failed to get token directly: {resp.text}")
                    return {"type": "credentials", "username": self.username, "password": self.password}
                except:
                    logger.error(f"Failed to parse authentication response: {resp.text}")
                    return {"type": "credentials", "username": self.username, "password": self.password}
            else:
                logger.error(f"Authentication failed with status {resp.status_code}: {resp.text}")
                return {"type": "credentials", "username": self.username, "password": self.password}
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {"type": "credentials", "username": self.username, "password": self.password}
    
    def refresh_token(self):
        """Force a token refresh"""
        self.last_auth_time = None  # Reset last auth time to force new auth
        return self.get_token_data()
    
    def get_auth_status(self):
        """Get authentication status"""
        status = {
            "authenticated": bool(self.auth_token),
            "auth_method": "direct_api",
            "last_auth_time": self.last_auth_time.isoformat() if self.last_auth_time else None
        }
        
        if self.last_auth_time:
            expiry = self.last_auth_time + timedelta(hours=6)
            status["expires_at"] = expiry.isoformat()
            
            remaining = expiry - datetime.now()
            if remaining.total_seconds() > 0:
                status["time_remaining"] = f"{remaining.seconds//3600}h {(remaining.seconds//60)%60}m"
            else:
                status["authenticated"] = False
                status["time_remaining"] = "Expired"
        
        return status

class TokenFileStrategy(AuthStrategy):
    """Authentication using a token file"""
    
    def __init__(self, token_file=None):
        self.token_file = token_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "iracing_token.json"
        )
        self.token_data = None
        self.last_load_time = None
        
        # Try to load token file initially
        self._load_token_file()
    
    def _load_token_file(self):
        """Load token data from file"""
        try:
            if not os.path.exists(self.token_file):
                logger.warning(f"Token file not found: {self.token_file}")
                return None
            
            with open(self.token_file, 'r') as f:
                self.token_data = json.load(f)
                self.last_load_time = datetime.now()
                logger.debug(f"Loaded token data from file, type: {self.token_data.get('type')}")
                return self.token_data
        except Exception as e:
            logger.error(f"Error loading token file: {e}")
            return None
    
    def get_token_data(self):
        """Get token data from file"""
        # Check if we need to reload the file (more than 5 minutes since last load)
        if not self.last_load_time or datetime.now() - self.last_load_time > timedelta(minutes=5):
            self._load_token_file()
        
        return self.token_data
    
    def refresh_token(self):
        """Force a token file reload"""
        return self._load_token_file()
    
    def get_auth_status(self):
        """Get authentication status"""
        token_data = self.get_token_data()
        
        status = {
            "authenticated": False,
            "auth_method": "none",
            "last_auth_time": None
        }
        
        if not token_data:
            return status
        
        # Check token type
        token_type = token_data.get("type")
        
        if token_type == "bearer":
            status["auth_method"] = "bearer_token"
            status["authenticated"] = True
        elif token_type == "cookie":
            status["auth_method"] = "cookie"
            status["authenticated"] = True
        elif token_type == "credentials":
            status["auth_method"] = "credentials"
            status["authenticated"] = False  # Credentials require interactive login
        
        # Get timestamp
        if "timestamp" in token_data:
            try:
                timestamp = datetime.fromisoformat(token_data["timestamp"])
                status["last_auth_time"] = token_data["timestamp"]
                
                # Calculate expiry (7 days for tokens)
                expiry = timestamp + timedelta(days=7)
                status["expires_at"] = expiry.isoformat()
                
                remaining = expiry - datetime.now()
                if remaining.total_seconds() > 0:
                    status["time_remaining"] = f"{remaining.days}d {remaining.seconds//3600}h {(remaining.seconds//60)%60}m"
                else:
                    status["authenticated"] = False
                    status["time_remaining"] = "Expired"
            except:
                pass
        
        return status

class CookieAuthStrategy(AuthStrategy):
    """Authentication using a cookie value from the iracing_token.json file"""
    
    def __init__(self):
        self.token_strategy = TokenFileStrategy()
    
    def get_token_data(self):
        """Get token data focusing on cookie authentication"""
        token_data = self.token_strategy.get_token_data()
        
        # If we have cookie-based authentication data, return it
        if token_data and token_data.get("type") == "cookie":
            return token_data
        
        # If we have other authentication data, convert it to cookie format if possible
        if token_data and token_data.get("type") == "bearer":
            # No direct conversion from bearer to cookie
            return token_data
        
        # For credentials, we can't automatically convert to cookie
        return token_data
    
    def refresh_token(self):
        """Force a token refresh"""
        return self.token_strategy.refresh_token()
    
    def get_auth_status(self):
        """Get authentication status"""
        status = self.token_strategy.get_auth_status()
        
        # Override auth method to cookie-specific
        if status["auth_method"] == "cookie":
            status["auth_method"] = "cookie"
        
        return status

def get_auth_strategy():
    """Factory function to get the appropriate authentication strategy based on environment"""
    strategy_name = os.getenv("AUTH_STRATEGY", "token_file").lower()
    
    if strategy_name == "api_direct":
        return DirectApiStrategy()
    elif strategy_name == "cookie":
        return CookieAuthStrategy()
    else:  # Default to token_file
        return TokenFileStrategy()

# Backwards compatibility - provides a simple CLI for updating token
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
    
    print("\nWhich authentication method would you like to use?")
    print("1. Cookie-based authentication (recommended for CAPTCHA issues)")
    print("2. Direct credentials (for backward compatibility)")
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        # Prompt for cookie-based auth
        print("\nTo generate a cookie token, you'll need to:")
        print("1. Log in to iRacing in your browser")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Application tab -> Cookies")
        print("4. Find the 'irsso_membersv2' cookie")
        print("5. Copy its value\n")
        
        username = input("Enter your iRacing email: ")
        cookie_value = input("Enter the irsso_membersv2 cookie value: ")
        
        # Create a token file with cookie credentials
        token_data = {
            "type": "cookie",
            "name": "irsso_membersv2",
            "value": cookie_value,
            "timestamp": datetime.now().isoformat(),
            "username": username
        }
    else:
        # Use direct credentials
        username = input("\nEnter your iRacing email: ")
        password = input("Enter your iRacing password: ")
        
        # Create a token file with direct credentials
        token_data = {
            "type": "credentials",
            "username": username,
            "password": password,
            "timestamp": datetime.now().isoformat()
        }
    
    # Save the token file
    with open(token_file, 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print(f"\nSaved token data to {token_file}")
    
    # Check if running in Docker and offer to restart
    try:
        import subprocess
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
    if choice == "1":
        print("1. The collector will now use your cookie token to authenticate")
        print("2. This token typically expires after 7 days, after which you'll need to generate a new one")
    else:
        print("1. The collector will now use your credentials directly to authenticate")
        print("2. If you encounter CAPTCHA issues, switch to cookie-based authentication")
    print("3. If you're still seeing authentication errors, check for rate limiting (429 errors)")

if __name__ == "__main__":
    main()