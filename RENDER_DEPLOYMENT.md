# Render Deployment Guide

## Overview
This guide explains how to deploy your Vedic Astrology Dashboard to Render. The keep-alive service automatically detects your Render URL and prevents inactivity timeouts.

## Deployment Steps

### 1. Create a Render Account
- Go to [render.com](https://render.com)
- Sign up for a free account

### 2. Create a New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select the `CleanAstroApp` directory as the root directory

### 3. Configure the Web Service

#### Build Command:
```bash
pip install -r requirements.txt
```

#### Start Command:
```bash
python app.py
```

#### Environment Variables:
Add this environment variable in your Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Set Flask to production mode |

**Note**: The keep-alive service will automatically detect your Render URL from Render's environment variables, so you don't need to set `RENDER_APP_URL` manually.

### 4. Automatic Keep-Alive Service

The keep-alive service will automatically start when deployed to Render and will:

- ✅ Auto-detect your Render app URL
- ✅ Ping your app every 40 seconds
- ✅ Prevent 50-second inactivity timeouts
- ✅ Run in a background thread
- ✅ Log all ping attempts

### 5. Environment Variable Setup

1. Go to your Render dashboard
2. Select your web service
3. Go to "Environment" tab
4. Add the environment variable:

```
FLASK_ENV=production
```

**That's it!** The keep-alive service will automatically detect your Render URL.

### 6. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your app
3. Wait for the build to complete (usually 2-3 minutes)

### 7. Verify Keep-Alive Service

After deployment, check your Render logs to see if the keep-alive service started:

```
🚀 Starting Vedic Astrology Dashboard...
Detected Render URL: https://your-app-name.onrender.com
✅ Keep-alive service started successfully
⏰ Will ping every 40 seconds to prevent inactivity timeout
✅ Ping successful at 12:34:56
```

## How Auto-Detection Works

The keep-alive service automatically detects your Render URL by checking these environment variables (in order):

1. `RENDER_EXTERNAL_URL` - Direct URL provided by Render
2. `RENDER_APP_NAME` + `RENDER_SERVICE_NAME` - Constructs URL from app/service names
3. `RENDER_APP_URL` - Manual override (if you want to set it manually)

## Troubleshooting

### Keep-Alive Not Starting
- Check Render logs for auto-detection messages
- Verify the app is deployed successfully
- Look for any error messages in the logs

### App Still Timing Out
- Check that the auto-detected URL is correct
- Verify the app is responding to HTTP requests
- Check keep-alive service logs for ping status

### Local Testing
The keep-alive service won't start locally unless you manually set the URL:

```bash
# Optional: Set environment variable for local testing
export RENDER_APP_URL=https://your-app-name.onrender.com

# Run the app
python app.py
```

## Features

### Automatic Keep-Alive
- ✅ Auto-detects Render URL from environment
- ✅ Pings every 40 seconds (before 50-second timeout)
- ✅ Runs in background thread (doesn't block main app)
- ✅ Comprehensive logging
- ✅ Error handling and retry logic

### Logging
The keep-alive service provides detailed logs:
- ✅ URL auto-detection messages
- ✅ Successful pings
- ⚠️ Warning for non-200 responses
- ❌ Error messages for failed requests

### Configuration
- Zero configuration required
- Automatic detection of Render environment
- Graceful handling of missing configuration
- Manual override option available

## Cost Optimization

The keep-alive service is designed to be efficient:
- Minimal resource usage
- Only pings when needed
- Automatic cleanup on app shutdown
- No external dependencies beyond `requests`

## Security

- Only makes GET requests to your own app
- No sensitive data transmitted
- Uses standard HTTP requests
- Timeout protection (10 seconds per request)

## Monitoring

Monitor your keep-alive service through:
1. Render logs (real-time)
2. App response times
3. Uptime monitoring
4. Error rate tracking

## Support

If you encounter issues:
1. Check Render logs for auto-detection messages
2. Verify the detected URL is correct
3. Test the app URL manually
4. Review the keep-alive service logs 