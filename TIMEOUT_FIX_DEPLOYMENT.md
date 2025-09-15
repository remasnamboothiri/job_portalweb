# Timeout Fix Deployment Guide

## Issues Fixed

1. **NVIDIA API Timeout**: Added 20-second timeout to AI API calls
2. **Gunicorn Worker Timeout**: Increased worker timeout to 60 seconds
3. **Error Handling**: Added graceful fallback responses when AI fails
4. **Request Monitoring**: Added middleware to log slow requests
5. **Health Checks**: Added endpoints to monitor application health

## Files Modified/Created

### 1. AI Integration (`jobapp/utils/interview_ai_nvidia.py`)
- Added proper timeout handling (20 seconds)
- Added fallback responses when AI API fails
- Reduced max_tokens for faster responses
- Better error logging

### 2. Gunicorn Configuration (`gunicorn.conf.py`)
- Increased timeout to 60 seconds
- Optimized worker settings
- Added memory management settings

### 3. Middleware (`jobapp/middleware.py`)
- `TimeoutHandlingMiddleware`: Handles timeout errors gracefully
- `RequestLoggingMiddleware`: Logs slow requests for monitoring

### 4. Environment Variables (`.env`)
```
GUNICORN_TIMEOUT=60
AI_API_TIMEOUT=20
WORKER_TIMEOUT=60
```

### 5. Health Checks (`jobapp/health.py`)
- `/health/` - Application health status
- `/ready/` - Deployment readiness check

### 6. Deployment Configuration (`render.yaml`)
- Updated Gunicorn command with proper timeout settings
- Added worker and request limits

## Deployment Steps

### 1. Update Environment Variables
Add these to your Render environment variables:
```
GUNICORN_TIMEOUT=60
AI_API_TIMEOUT=20
WORKER_TIMEOUT=60
```

### 2. Deploy with New Configuration
The updated `render.yaml` will automatically use the new Gunicorn settings:
```bash
gunicorn job_platform.wsgi:application --bind 0.0.0.0:$PORT --timeout 60 --workers 2 --max-requests 1000 --max-requests-jitter 100
```

### 3. Monitor Health
After deployment, check:
- `/health/` - Overall application health
- `/ready/` - Deployment readiness
- Monitor logs for slow request warnings

## Expected Improvements

1. **Reduced Timeouts**: AI requests will timeout after 20 seconds instead of hanging
2. **Graceful Fallbacks**: When AI fails, users get predefined interview questions
3. **Better Monitoring**: Slow requests are logged for optimization
4. **Stable Workers**: Gunicorn workers won't be killed prematurely
5. **Health Visibility**: Easy monitoring of application status

## Testing

1. **Test AI Timeout**: 
   - Start an interview
   - If NVIDIA API is slow/down, should get fallback responses

2. **Test Health Endpoints**:
   ```bash
   curl https://your-app.onrender.com/health/
   curl https://your-app.onrender.com/ready/
   ```

3. **Monitor Logs**:
   - Look for "AI API Error" messages (fallbacks working)
   - Look for "Slow request" warnings (performance monitoring)

## Rollback Plan

If issues occur, you can quickly rollback by:
1. Reverting the `render.yaml` startCommand to the original
2. Removing the new middleware from `settings.py`
3. Using the original `interview_ai_nvidia.py` file

## Next Steps

1. Monitor application performance after deployment
2. Adjust timeout values if needed based on actual API response times
3. Consider implementing async processing for AI requests if timeouts persist
4. Set up external monitoring using the health check endpoints