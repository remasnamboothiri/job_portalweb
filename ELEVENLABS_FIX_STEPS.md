# ElevenLabs API Key Fix - Step by Step

## Current Issue
```
ElevenLabs API error: 401
"missing_permissions: text_to_speech"
```

## Solution: Get New Free API Key

### Step 1: Create Free ElevenLabs Account
1. Go to: https://elevenlabs.io/
2. Click "Sign Up" (it's FREE)
3. Verify your email

### Step 2: Get API Key
1. Login to ElevenLabs
2. Click your profile (top right)
3. Go to "Profile" → "API Key"
4. Click "Create API Key"
5. Copy the new key

### Step 3: Update Your Project
Replace in your `.env` file:
```
ELEVENLABS_API_KEY=your_new_api_key_here
```

### Step 4: Restore Original Voice ID
After getting the new key, you can try the original voice ID:
```python
"voice_id": "EaBs7G1VibMrNAuz2Na7"
```

## Free Plan Limits
- 10,000 characters per month
- Access to standard voices
- Perfect for testing and small projects

## Alternative: Keep Using gTTS
Your system already works perfectly with gTTS fallback. If you don't want to get a new API key, just remove the ElevenLabs key from `.env`:
```
# ELEVENLABS_API_KEY=  # Comment out this line
```

The system will automatically use gTTS for all voice generation.

## Test After Fix
Run: `python test_new_voice.py`
Should show: "ElevenLabs TTS successful" instead of "gTTS fallback"