"""
iRacing Authentication Helper Module - Direct Version

This module provides a direct authentication method for the iRacing Data API
that works around the CAPTCHA requirements.
"""

import os
import json
import base64
import hashlib
import logging
import traceback
import aiohttp
import asyncio
import time
from datetime import datetime, timedelta

logger = logging.getLogger("iracing_auth")

class iRacingAuth:
    """Handles authentication with the iRacing Data API using direct credentials"""
    
    BASE_URL = "https://members-ng.iracing.com"
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = None
        self.auth_token = None
        self.auth_headers = {
            "User-Agent": "iRacing-Grafana-Observability/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Load token if available
        self._load_token_from_file()
        
    def _load_token_from_file(self):
        """Load token data from file if available"""
        try:
            # Look for token file
            token_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "iracing_token.json")
            token_file_alt = "./iracing_token.json"
            
            # Try both possible locations
            if os.path.exists(token_file):
                file_path = token_file
            elif os.path.exists(token_file_alt):
                file_path = token_file_alt
            else:
                logger.warning("No token file found")
                return
                
            with open(file_path, 'r') as f:
                token_data = json.load(f)
                
            # Check if credentials are available and use them
            if token_data.get("type") == "credentials":
                self.username = token_data.get("username", self.username)
                self.password = token_data.get("password", self.password)
                logger.info(f"Loaded credentials from token file: {self.username}")
        except Exception as e:
            logger.error(f"Error loading token file: {e}")
            
    async def initialize(self):
        """Initialize the session"""
        self.session = aiohttp.ClientSession()
        logger.info("Session initialized")
        return self
        
    async def authenticate(self):
        """Auth is handled directly in get_data now"""
        logger.info("Direct authentication will be handled per request")
        return True
        
    async def get_data(self, endpoint, params=None):
        """Make a request to the API with direct authentication"""
        # Starting with a delay to handle rate limiting
        await asyncio.sleep(1)
        
        url = f"{self.BASE_URL}/{endpoint}" if not endpoint.startswith("http") else endpoint
        
        # Hash password for auth
        email_lower = self.username.lower()
        hash_input = f"{self.password}{email_lower}"
        hash_bytes = hashlib.sha256(hash_input.encode('utf-8')).digest()
        encoded_password = base64.b64encode(hash_bytes).decode('utf-8')
        
        # Auth data
        auth_data = {
            "email": self.username,
            "password": encoded_password
        }
        
        try:
            # First authenticate to get cookies
            async with self.session.post(
                f"{self.BASE_URL}/auth",
                json=auth_data,
                headers=self.auth_headers
            ) as auth_response:
                if auth_response.status != 200:
                    logger.error(f"Auth failed: {auth_response.status}")
                    # Add delay for rate limiting
                    await asyncio.sleep(5)
                    return None
                    
                # Now make the actual request with the authenticated session
                async with self.session.get(
                    url,
                    params=params,
                    headers=self.auth_headers
                ) as response:
                    if response.status == 200:
                        try:
                            # Handle link response
                            response_text = await response.text()
                            try:
                                data = json.loads(response_text)
                                
                                # Check if it's a link to cached data
                                if "link" in data and isinstance(data["link"], str):
                                    cache_link = data["link"]
                                    logger.debug(f"Retrieved cache link: {cache_link}")
                                    
                                    # Get actual data
                                    async with self.session.get(cache_link) as cache_response:
                                        if cache_response.status == 200:
                                            try:
                                                return await cache_response.json()
                                            except:
                                                logger.error("Error parsing cache response")
                                                return None
                                        else:
                                            logger.error(f"Cache link request failed: {cache_response.status}")
                                            return None
                                else:
                                    # Regular data
                                    return data
                            except json.JSONDecodeError:
                                # Not JSON
                                return response_text
                        except:
                            logger.warning(f"Could not read response from {endpoint}")
                            return None
                    elif response.status == 429:
                        # Rate limited, add longer delay
                        logger.warning(f"Rate limited (429) for endpoint: {endpoint}")
                        await asyncio.sleep(10)
                        return None
                    else:
                        logger.error(f"Request failed: {response.status}")
                        await asyncio.sleep(2)
                        return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            logger.debug(f"Request error details: {traceback.format_exc()}")
            return None
            
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()