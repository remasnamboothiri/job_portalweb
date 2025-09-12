# Chatterbox Model Migration Summary

## Overview
Successfully migrated the TTS system from using the Kokkoro model to using the **Chatterbox model** with the **female_default voice** as requested.

## Changes Made

### 1. TTS Configuration Updates (`jobapp/tts.py`)

#### Updated Voice Configuration:
- **BUILTIN_VOICES**: Added configuration for `female_default` voice with the specified audio URL
- **AVAILABLE_VOICES**: Updated to use chatterbox model with female_default voice
- **Default Model**: Changed from `kokkoro` to `chatterbox`

#### Key Configuration:
```python
BUILTIN_VOICES = {
    "female_default": {
        "voice_id": "female_default",
        "name": "Female Default",
        "description": "Professional female voice",
        "audio_url": "https://storage.googleapis.com/chatterbox-demo-samples/prompts/female_shadowheart4.flac",
        "type": "builtin",
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### Updated API Payload:
```python
payload = {
    "input": {
        "text": text,
        "model": "chatterbox",  # Specify chatterbox model
        "voice_id": "female_default",  # Use female_default voice
        "jwt_token": JWT_SECRET,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
}
```

### 2. Function Updates

#### Renamed Functions:
- `test_kokkoro_voice()` → `test_chatterbox_voice()`
- `generate_tts_kokkoro()` → `generate_tts_chatterbox()`
- Added `generate_tts_female_default()` function

#### Updated Default Parameters:
- `generate_tts()`: Default model changed from `"kokkoro"` to `"chatterbox"`
- `generate_runpod_tts()`: Default model changed from `"kokkoro"` to `"chatterbox"`

### 3. View Updates (`jobapp/views.py`)

#### Updated Test Functions:
- `test_kokkoro_voice()` → `test_chatterbox_voice()`
- Updated debug functions to reference chatterbox model
- Updated test messages to reflect female_default voice

### 4. URL Pattern Updates (`jobapp/urls.py`)

#### Updated Endpoints:
- `test-kokkoro/` → `test-chatterbox/`
- URL name: `test_kokkoro_voice` → `test_chatterbox_voice`

### 5. File Naming Updates

#### Cache File Naming:
- Files now saved as: `runpod_chatterbox_female_default_{hash}.mp3`
- Hash includes "chatterbox_female_default" for proper caching

## Testing

### Created Test Script:
- `test_chatterbox_config.py`: Comprehensive test script to verify configuration

### Test Endpoints Available:
1. `/test-chatterbox/` - Test chatterbox voice specifically
2. `/debug-tts/` - Debug TTS system with chatterbox model
3. `/test-tts/` - General TTS testing
4. `/generate-audio/` - Generate audio with chatterbox model

## API Configuration

### RunPod Endpoint:
- **Endpoint**: `https://api.runpod.ai/v2/p3eso571qdfug9/runsync`
- **Model**: `chatterbox`
- **Voice**: `female_default`
- **Voice Settings**: 
  - Stability: 0.75
  - Similarity Boost: 0.75

## Verification Steps

1. **Run the test script**:
   ```bash
   cd job_platform
   python test_chatterbox_config.py
   ```

2. **Test via web interface**:
   - Visit `/test-chatterbox/` to test the voice
   - Visit `/debug-tts/` to check system health

3. **Test in interview**:
   - Start an interview and verify the voice uses female_default from chatterbox model

## Fallback Chain

The system maintains a robust fallback chain:
1. **Primary**: RunPod chatterbox model with female_default voice
2. **Fallback**: gTTS (Google Text-to-Speech)
3. **Emergency**: Text-only response

## Environment Variables Required

Ensure these are set in your environment:
- `RUNPOD_API_KEY`: Your RunPod API key
- `JWT_SECRET`: JWT secret for authentication

## Notes

- All existing functionality is preserved
- Backward compatibility maintained through function aliases
- Caching system updated to use new model/voice combination
- Error handling and logging updated to reflect new configuration
- The system will automatically use female_default voice when using chatterbox model

## Files Modified

1. `jobapp/tts.py` - Main TTS configuration and functions
2. `jobapp/views.py` - View functions for testing and debugging
3. `jobapp/urls.py` - URL patterns for test endpoints
4. `test_chatterbox_config.py` - New test script (created)
5. `CHATTERBOX_MIGRATION_SUMMARY.md` - This documentation (created)

The migration is complete and the system is now configured to use the Kokkoro endpoint with the chatterbox model and female_default voice as requested.