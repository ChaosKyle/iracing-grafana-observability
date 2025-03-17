# iRacing Authentication Guide

## Important Authentication Update (March 2025)

As of March 2025, the iRacing API now requires CAPTCHA verification during login, which means automated login through traditional username/password methods no longer works without manual intervention.

## How to Authenticate with the Collector

### Manual Token Generation

1. Run the authentication helper script:
   ```bash
   python python/get_iracing_token.py
   ```

2. Enter your iRacing email and password when prompted

3. The script will attempt to authenticate. When it detects CAPTCHA requirements, it will:
   - Open a browser window to the iRacing login page
   - Prompt you to log in manually through the browser
   - Ask you to copy the authentication cookie value

4. After logging in, obtain the authentication cookie:
   - In Chrome: Open DevTools (F12) → Application → Cookies → https://members.iracing.com
   - Find the cookie named `irsso_membersv2`
   - Copy its value
   - Paste the value back into the terminal prompt

5. The script will save the cookie value to `python/iracing_token.json`

6. Restart the collector to use the new token:
   ```bash
   docker-compose restart collector
   ```

### Token Expiration

iRacing authentication tokens typically expire after about 7 days. When this happens:
- The collector logs will show authentication errors
- You'll need to regenerate the token using the steps above

## Technical Details

### How the Authentication Works

1. The original API required username/password authentication directly
2. Recent security updates from iRacing now require CAPTCHA verification
3. Our workaround uses:
   - A manual browser login (where you complete the CAPTCHA)
   - The authentication cookie from that session
   - This cookie is used for subsequent API requests

### Authentication Flow

1. Manual login with CAPTCHA → Cookie obtained
2. Cookie stored in `iracing_token.json`
3. Collector uses this cookie for API requests
4. If cookie expires, return to step 1

## Troubleshooting

### Common Authentication Issues

1. **"Authentication requires CAPTCHA verification"**:
   - Run the `get_iracing_token.py` script to generate a new token

2. **Token expires frequently**:
   - This is normal behavior - tokens last ~7 days
   - iRacing's security policy determines token duration
   
3. **"Failed to load token from file"**:
   - Ensure `iracing_token.json` exists in the correct location
   - Check file permissions

4. **Browser login not working**:
   - Try logging in manually at [iRacing Members Site](https://members.iracing.com)
   - Copy the cookie manually from your browser's developer tools
   - Create a JSON file at `python/iracing_token.json` with the following structure:
     ```json
     {
       "type": "cookie",
       "name": "irsso_membersv2",
       "value": "YOUR_COOKIE_VALUE_HERE",
       "timestamp": "2025-03-09T00:00:00.000Z",
       "username": "your_email@example.com"
     }
     ```

## Best Practices

1. **Security**:
   - Never share your token or cookie values
   - The token provides access to your iRacing account data
   
2. **Automation**:
   - Consider setting a calendar reminder to refresh your token weekly
   - For team setups, you may need to coordinate token refreshes