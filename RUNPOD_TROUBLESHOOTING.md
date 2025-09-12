# RunPod TTS Troubleshooting Guide

## Issue: Getting Google TTS instead of RunPod Chatterbox Voice

If you're hearing Google TTS instead of the RunPod chatterbox voice, the system is falling back to gTTS because the RunPod API call is failing.

## Quick Diagnosis Steps

### 1. Check Environment Variables
```bash
# In your terminal or check your .env file
echo $RUNPOD_API_KEY
echo $JWT_SECRET
```

### 2. Test RunPod API Directly
```bash
cd job_platform
python debug_runpod.py
```

### 3. Test RunPod Function Only
```bash
cd job_platform
python test_runpod_only.py
```

### 4. Test via Web Interface
Visit these URLs in your browser:
- `/debug-tts/` - Full system debug
- `/test-chatterbox/?force_runpod=true` - Force RunPod only test

## Common Issues and Solutions

### Issue 1: Missing API Credentials
**Symptoms:** Logs show "RunPod credentials missing"
**Solution:** 
1. Check your `.env` file has:
   ```
   RUNPOD_API_KEY=your_actual_api_key_here
   JWT_SECRET=your_actual_jwt_secret_here
   ```
2. Restart your Django server after adding credentials

### Issue 2: Wrong API Endpoint
**Symptoms:** HTTP 404 or connection errors
**Solution:** Verify the endpoint URL in `jobapp/tts.py`:
```python
RUNPOD_ENDPOINT = "https://api.runpod.ai/v2/p3eso571qdfug9/runsync"
```

### Issue 3: Wrong Model/Voice Configuration
**Symptoms:** API returns error about unknown model or voice
**Solution:** Check if your RunPod endpoint supports:
- Model: `chatterbox`
- Voice: `female_default`

### Issue 4: API Authentication Issues
**Symptoms:** HTTP 401 or 403 errors
**Solution:**
1. Verify your RUNPOD_API_KEY is correct
2. Check if your JWT_SECRET matches what the endpoint expects
3. Ensure your RunPod account has sufficient credits

### Issue 5: Payload Format Issues
**Symptoms:** API returns 400 Bad Request
**Solution:** The current payload format is:
```json
{
  "input": {
    "text": "Your text here",
    "model": "chatterbox",
    "voice_id": "female_default",
    "jwt_token": "your_jwt_secret"
  }
}
```

## Debugging Commands

### 1. Check System Health
```python
from jobapp.tts import check_tts_system
health = check_tts_system()
print(health)
```

### 2. Test Direct API Call
```python
from jobapp.tts import generate_runpod_tts
result = generate_runpod_tts("Hello test", "chatterbox")
print(f"Result: {result}")
```

### 3. Force RunPod (No Fallback)
```python
from jobapp.tts import generate_tts
result = generate_tts("Hello test", model="chatterbox", force_runpod=True)
print(f"Result: {result}")
```

## Log Analysis

Look for these log messages:

### Success Indicators:
- `🚀 Attempting RunPod TTS with model: chatterbox`
- `✅ RunPod TTS successful: /media/tts/runpod_chatterbox_female_default_xxxxx.mp3`

### Failure Indicators:
- `⚠️ RunPod TTS failed, falling back to gTTS`
- `RunPod API error: 400/401/403/500`
- `No audio_base64 found in response`

## Testing Different Payload Formats

If the current format doesn't work, try these alternatives in `debug_runpod.py`:

### Format 1 (Current):
```json
{
  "input": {
    "text": "Hello",
    "model": "chatterbox",
    "voice_id": "female_default",
    "jwt_token": "your_jwt"
  }
}
```

### Format 2 (Alternative):
```json
{
  "input": {
    "text": "Hello",
    "voice_id": "female_default",
    "jwt_token": "your_jwt"
  }
}
```

### Format 3 (Simple):
```json
{
  "input": {
    "text": "Hello",
    "model": "chatterbox",
    "jwt_token": "your_jwt"
  }
}
```

## Contact RunPod Support

If none of the above works, contact RunPod support with:
1. Your endpoint ID: `p3eso571qdfug9`
2. The exact error messages from logs
3. The payload format you're using
4. Ask them to confirm:
   - Is the `chatterbox` model available?
   - Is the `female_default` voice available?
   - What's the correct payload format?

## Quick Fix: Force RunPod Usage

To temporarily disable gTTS fallback and force RunPod usage:

1. Edit `jobapp/tts.py`
2. In `generate_tts()` function, comment out the fallback:
```python
# Fallback to gTTS if RunPod fails
# logger.warning("⚠️ RunPod TTS failed, falling back to gTTS")
# return generate_gtts_fallback(clean_text)

# Instead, return None to see the actual error
logger.error("❌ RunPod TTS failed, no fallback")
return None
```

This will help you see the exact error instead of masking it with gTTS fallback.

## Files to Check

1. `jobapp/tts.py` - Main TTS configuration
2. `job_platform/settings.py` - Environment variables
3. `.env` - API credentials
4. Django logs - Error messages
5. Browser Network tab - API request/response details