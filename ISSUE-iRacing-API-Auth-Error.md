# iRacing API Authentication Guide

## Overview

The iRacing Data API now requires CAPTCHA verification during login, which prevents direct automation. This document explains how to solve authentication issues with the collector.

## Error Symptoms

If you see errors like the following in your logs, you're experiencing CAPTCHA authentication requirements:

```
- iracing_auth - ERROR - Authentication requires CAPTCHA verification. Cannot proceed with automated authentication.
- iracing_auth - ERROR - Failed to authenticate for API request
- iracing_collector - ERROR - Failed to retrieve driver information
```

## Solution

The collector now supports several authentication methods to work around the CAPTCHA requirement:

1. **Cookie-based authentication** (recommended): Manually log in once to get a cookie that lasts about 7 days
2. **Bearer token authentication**: Automatically tries to get a token without CAPTCHA (may not always work)
3. **Fallback credential authentication**: Stores credentials for the dashboard UI to guide manual authentication

## How to Generate a Token

### Method 1: Using the Command Line Script (Recommended)

1. Run the token generation script:
   ```bash
   # On Linux/macOS
   ./scripts/generate-token.sh
   
   # On Windows
   python python/get_iracing_token.py
   ```

2. Enter your iRacing credentials when prompted

3. If CAPTCHA verification is required, the script will:
   - Open a browser window for you to log in manually
   - Prompt you to copy the authentication cookie after login
   - Save the cookie as a token for future authentication

### Method 2: Using the Web Dashboard

1. Access the collector's web dashboard at `http://localhost:8080`

2. Click the "Generate New Token" button 

3. Follow the guided process to obtain and save a new authentication token

## Docker Configuration

The docker-compose.yml has been updated with new environment variables to control authentication:

```yaml
environment:
  # Authentication options
  IRACING_USERNAME: ${IRACING_USERNAME}
  IRACING_PASSWORD: ${IRACING_PASSWORD}
  
  # Optional direct token configuration
  IRACING_TOKEN: ${IRACING_TOKEN:-""}
  
  # Auth strategy: token_file (default), api_direct, cookie
  AUTH_STRATEGY: ${AUTH_STRATEGY:-"token_file"}
  
  # Token refresh schedule (cron format)
  TOKEN_REFRESH_SCHEDULE: ${TOKEN_REFRESH_SCHEDULE:-"0 0 * * *"}
```

## Token Expiration

Tokens typically expire after approximately 7 days. When a token expires:

1. The collector will automatically try to refresh using the configured strategy
2. If CAPTCHA verification is required, you'll need to manually generate a new token
3. The dashboard will show authentication status and token expiration information

## Troubleshooting

If you continue to experience authentication issues:

1. Check the authentication status on the dashboard (`http://localhost:8080`)
2. Generate a fresh token using one of the methods above
3. Ensure your iRacing credentials are correct
4. Check for rate limiting (HTTP 429 errors) and wait a few minutes before retrying
5. Make sure your token file has the correct permissions (readable by the collector user)

For persistent issues, review the collector logs for detailed error messages.