"""
iRacing Authentication Helper Module

This module provides functions to authenticate with the iRacing Data API
and maintain a valid authentication session.
"""

import os
import json
import base64
import hashlib
import logging
import traceback
import aiohttp
import asyncio
from datetime import datetime, timedelta
from yarl import URL

logger = logging.getLogger("iracing_auth")

class iRacingAuth:
    """Handles authentication with the iRacing Data API"""
    
    BASE_URL = "https://members-ng.iracing.com"
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
        # Store credentials for basic auth
        self.auth = aiohttp.BasicAuth(login=username, password=password)
        
        self.session = None
        self.auth_token = None
        self.last_auth_time = None
        self.auth_expiry = None  # Default 1 hour session expiry
        
    async def initialize(self):
        """Initialize the session and authenticate"""
        # Create a session with basic auth
        self.session = aiohttp.ClientSession(auth=self.auth)
        
        # Try to authenticate
        auth_success = await self.authenticate()
        if not auth_success:
            logger.error("Failed initial authentication attempt")
        return self
    
    async def authenticate(self):
        """Authenticate with the iRacing Data API using the official API method"""
        logger.info("Authenticating with iRacing Data API...")
        
        try:
            # Close any existing session
            if self.session:
                await self.session.close()
            
            # Create a new session
            self.session = aiohttp.ClientSession()
            
            # Use iRacing's documented authentication method
            login_url = f"{self.BASE_URL}/auth"
            
            # Prepare the properly hashed password according to iRacing documentation
            # 1. Convert email to lowercase
            email_lower = self.username.lower()
            
            # 2. SHA-256 hash the password + lowercase email
            hash_input = f"{self.password}{email_lower}"
            hash_bytes = hashlib.sha256(hash_input.encode('utf-8')).digest()
            
            # 3. Base64 encode the hash
            encoded_password = base64.b64encode(hash_bytes).decode('utf-8')
            
            # Prepare the authentication JSON payload
            auth_data = {
                "email": self.username,
                "password": encoded_password
            }
            
            # Set proper headers
            headers = {
                "User-Agent": "iRacing-Grafana-Observability/1.0",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Make the authentication request
            async with self.session.post(login_url, json=auth_data, headers=headers) as response:
                # Get response status and content for debugging
                status = response.status
                try:
                    response_text = await response.text()
                    logger.debug(f"Auth response: {status}, content: {response_text[:200]}")
                    
                    # Try to parse the response if it's JSON
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check for verification requirements
                        if response_data.get("verificationRequired", False):
                            logger.error("Authentication requires CAPTCHA verification. Cannot proceed with automated authentication.")
                            return False
                        
                        # Check for auth token in response
                        if "authcode" in response_data and response_data["authcode"] != 0:
                            self.auth_token = response_data["authcode"]
                            logger.debug(f"Got auth token: {self.auth_token[:20]}...")
                    except json.JSONDecodeError:
                        logger.debug("Authentication response is not JSON")
                except:
                    logger.debug(f"Could not read auth response, status: {status}")
                
                # Check response status
                if status == 200:
                    # Check for cookies in the response
                    cookies = self.session.cookie_jar.filter_cookies(self.BASE_URL)
                    cookie_count = 0
                    for name, cookie in cookies.items():
                        cookie_count += 1
                        logger.debug(f"Cookie found: {name}")
                    
                    logger.info(f"Authentication successful, got {cookie_count} cookies")
                    
                    # Record authentication time
                    self.last_auth_time = datetime.now()
                    self.auth_expiry = self.last_auth_time + timedelta(minutes=55)
                    
                    # Test a simple API call to validate authentication
                    valid = await self._test_api_access()
                    if valid:
                        logger.info("API access validated successfully")
                        return True
                    else:
                        logger.error("Authentication succeeded but API access validation failed")
                        return False
                else:
                    logger.error(f"Authentication failed with status {status}")
                    return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            logger.debug(f"Authentication error details: {traceback.format_exc()}")
            return False
    
    async def _test_api_access(self):
        """Test API access to validate authentication"""
        try:
            # Try a simple API endpoint
            test_url = f"{self.BASE_URL}/data/lookup/seasons"
            
            headers = {
                "User-Agent": "iRacing-Grafana-Observability/1.0",
                "Accept": "application/json"
            }
            
            async with self.session.get(test_url, headers=headers) as response:
                if response.status == 200:
                    return True
                else:
                    try:
                        response_text = await response.text()
                        logger.error(f"API access test failed: {response.status}, Response: {response_text[:200]}")
                    except:
                        logger.error(f"API access test failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"API access test error: {e}")
            return False
    
    async def _validate_session(self):
        """Validate the session is working by making a test API call"""
        try:
            # Try to access a simple endpoint that requires authentication
            # Use a different endpoint that's more likely to work
            url = f"{self.BASE_URL}/data/lookup/seasons"
            
            async with self.session.get(
                url,
                headers=self._get_request_headers()
            ) as response:
                if response.status == 200:
                    logger.info("Session validation successful")
                    return True
                else:
                    error_content = await response.text()
                    logger.debug(f"Validation request failed: {response.status}, Response: {error_content}")
                    return False
        except Exception as e:
            logger.warning(f"Session validation error: {e}")
            return False
    
    async def ensure_authenticated(self):
        """Ensure the session is authenticated, re-authenticate if needed"""
        # Check if we need to refresh the authentication
        if not self.last_auth_time or datetime.now() > self.auth_expiry:
            logger.info("Authentication expired or not initialized, re-authenticating...")
            return await self.authenticate()
        
        # Check if the session is still valid
        is_valid = await self._validate_session()
        if not is_valid:
            logger.info("Session validation failed, re-authenticating...")
            return await self.authenticate()
        
        return True
    
    def _get_browser_headers(self):
        """Get headers for browser-like requests"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def _get_api_headers(self):
        """Get headers for API requests during authentication"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://members.iracing.com",
            "Referer": "https://members.iracing.com/membersite/login.jsp"
        }
    
    def _get_request_headers(self):
        """Get headers for authenticated API requests"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Add authorization header if we have a token
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        return headers
    
    async def get_data(self, endpoint, params=None):
        """Make an authenticated request to an API endpoint"""
        # Ensure we're authenticated before proceeding
        if not self.last_auth_time or datetime.now() > self.auth_expiry:
            logger.info("Authentication expired or not initialized, authenticating...")
            if not await self.authenticate():
                logger.error("Failed to authenticate for API request")
                return None
        
        # Make the API request
        if endpoint.startswith("http"):
            url = endpoint  # If full URL is provided
        else:
            url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            # Set proper headers for API request
            headers = {
                "User-Agent": "iRacing-Grafana-Observability/1.0",
                "Accept": "application/json"
            }
            
            # Add authorization header if we have a token
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            logger.debug(f"Making request to: {url}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                logger.debug(f"Response status: {response.status}")
                
                # Handle standard response
                if response.status == 200:
                    try:
                        # Check if this is a link response (iRacing API caching pattern)
                        response_text = await response.text()
                        
                        # Try to parse as JSON
                        try:
                            response_data = json.loads(response_text)
                            
                            # Check if this is a link response
                            if "link" in response_data and isinstance(response_data["link"], str):
                                # This is a cached data response, we need to fetch from the provided link
                                cache_link = response_data["link"]
                                logger.debug(f"Retrieved cache link: {cache_link}")
                                
                                # Fetch the actual data from the cache link
                                async with self.session.get(cache_link) as cache_response:
                                    if cache_response.status == 200:
                                        try:
                                            cache_data = await cache_response.json()
                                            logger.debug(f"Successfully retrieved data from cache link")
                                            return cache_data
                                        except:
                                            logger.error("Failed to parse cache response as JSON")
                                            return None
                                    else:
                                        logger.error(f"Failed to retrieve data from cache link: {cache_response.status}")
                                        return None
                            else:
                                # Regular data response
                                logger.debug(f"Successfully received data from {endpoint}")
                                return response_data
                                
                        except json.JSONDecodeError:
                            # Not JSON, return as text
                            logger.debug(f"Received non-JSON response from {endpoint}")
                            return response_text
                    except:
                        logger.warning(f"Could not read response from {endpoint}")
                        return None
                    
                # Handle authentication errors    
                elif response.status == 401 or response.status == 403:
                    # Authentication error, try to re-authenticate
                    try:
                        error_text = await response.text()
                        logger.warning(f"Authentication error for {endpoint}: {response.status}, Response: {error_text}")
                    except:
                        logger.warning(f"Authentication error for {endpoint}: {response.status}")
                    
                    # Try to re-authenticate
                    logger.info("Re-authenticating...")
                    if await self.authenticate():
                        # Retry with new authentication
                        logger.info("Retrying request after re-authentication")
                        
                        # Update headers with new authentication
                        if self.auth_token:
                            headers["Authorization"] = f"Bearer {self.auth_token}"
                        
                        # Retry the request
                        async with self.session.get(url, params=params, headers=headers) as retry_response:
                            if retry_response.status == 200:
                                try:
                                    # Check for link response
                                    retry_text = await retry_response.text()
                                    
                                    try:
                                        retry_data = json.loads(retry_text)
                                        
                                        # Check if this is a link response
                                        if "link" in retry_data and isinstance(retry_data["link"], str):
                                            # This is a cached data response, fetch from the provided link
                                            cache_link = retry_data["link"]
                                            logger.debug(f"Retrieved cache link after retry: {cache_link}")
                                            
                                            # Fetch the actual data from the cache link
                                            async with self.session.get(cache_link) as cache_response:
                                                if cache_response.status == 200:
                                                    try:
                                                        cache_data = await cache_response.json()
                                                        logger.debug(f"Successfully retrieved data from cache link after retry")
                                                        return cache_data
                                                    except:
                                                        logger.error("Failed to parse cache response as JSON after retry")
                                                        return None
                                                else:
                                                    logger.error(f"Failed to retrieve data from cache link after retry: {cache_response.status}")
                                                    return None
                                        else:
                                            # Regular data response
                                            logger.debug(f"Successfully received data from {endpoint} after retry")
                                            return retry_data
                                            
                                    except json.JSONDecodeError:
                                        # Not JSON, return as text
                                        logger.debug(f"Received non-JSON response from {endpoint} after retry")
                                        return retry_text
                                except:
                                    logger.warning(f"Could not read retry response from {endpoint}")
                                    return None
                            else:
                                try:
                                    error_content = await retry_response.text()
                                    logger.error(f"API request failed after retry: {retry_response.status}, Response: {error_content}")
                                except:
                                    logger.error(f"API request failed after retry: {retry_response.status}")
                                return None
                    else:
                        logger.error("Re-authentication failed")
                        return None
                    
                # Handle rate limiting
                elif response.status == 429:
                    try:
                        error_text = await response.text()
                        logger.warning(f"Rate limit exceeded for {endpoint}: {response.status}, Response: {error_text}")
                        
                        # Check rate limit headers
                        limit = response.headers.get('x-ratelimit-limit', 'unknown')
                        remaining = response.headers.get('x-ratelimit-remaining', 'unknown')
                        reset = response.headers.get('x-ratelimit-reset', 'unknown')
                        
                        logger.warning(f"Rate limit info: limit={limit}, remaining={remaining}, reset={reset}")
                    except:
                        logger.warning(f"Rate limit exceeded for {endpoint}: {response.status}")
                    
                    return None
                    
                # Handle maintenance mode
                elif response.status == 503:
                    try:
                        error_text = await response.text()
                        logger.warning(f"Service maintenance for {endpoint}: {response.status}, Response: {error_text}")
                    except:
                        logger.warning(f"Service maintenance for {endpoint}: {response.status}")
                    
                    return None
                    
                # Handle other errors
                else:
                    try:
                        error_text = await response.text()
                        logger.error(f"API request failed for {endpoint}: {response.status}, Response: {error_text}")
                    except:
                        logger.error(f"API request failed for {endpoint}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"API request error for {endpoint}: {e}")
            logger.debug(f"API request error details: {traceback.format_exc()}")
            return None
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()