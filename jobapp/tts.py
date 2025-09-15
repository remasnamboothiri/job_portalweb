import requests
import os
from gtts import gTTS
from django.conf import settings
import hashlib
import logging

# Set up logging
logger = logging.getLogger(__name__)

# ElevenLabs TTS Configuration
ELEVENLABS_API_KEY = getattr(settings, 'ELEVENLABS_API_KEY', '')
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# ElevenLabs Female Voices Configuration
ELEVENLABS_VOICES = {
    "female_professional": {
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",  # George - Professional female voice
        "name": "Professional Female",
        "description": "Clean, professional female voice perfect for interviews",
        "type": "elevenlabs",
        "model": "eleven_multilingual_v2"
    },
    "female_friendly": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella - Friendly female voice
        "name": "Friendly Female", 
        "description": "Warm, friendly female voice",
        "type": "elevenlabs",
        "model": "eleven_multilingual_v2"
    }
}

# Available voice models
AVAILABLE_VOICES = ELEVENLABS_VOICES
AVAILABLE_MODELS = list(AVAILABLE_VOICES.keys())

# Validate environment variables
if not ELEVENLABS_API_KEY:
    logger.warning("ELEVENLABS_API_KEY not found in Django settings")
else:
    logger.info("ElevenLabs API key configured successfully")

def generate_elevenlabs_tts(text, voice="female_professional"):
    """
    Generate TTS audio using ElevenLabs API with female voice (direct API calls)
    """
    try:
        if not ELEVENLABS_API_KEY:
            logger.error("ElevenLabs API key not configured")
            return None
            
        # Validate voice
        if voice not in ELEVENLABS_VOICES:
            logger.warning(f"Invalid voice '{voice}', using 'female_professional'")
            voice = "female_professional"
        
        voice_config = ELEVENLABS_VOICES[voice]
        voice_id = voice_config["voice_id"]
        model_id = voice_config["model"]
        
        logger.info(f"ElevenLabs TTS generation with voice '{voice}' for: '{text[:50]}...'")
        
        # Create filename for caching
        text_hash = hashlib.md5(f"{text}_elevenlabs_{voice}".encode()).hexdigest()[:8]
        filename = f"elevenlabs_{voice}_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check if file already exists (caching)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            media_url = f"/media/tts/{filename}"
            logger.info(f"Using cached ElevenLabs TTS: {media_url}")
            return media_url
        
        # Prepare API request
        url = f"{ELEVENLABS_API_URL}/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        logger.info(f"Making request to ElevenLabs API: {url}")
        
        # Make API request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Save audio data directly
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Verify file was created and has content
            if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                media_url = f"/media/tts/{filename}"
                logger.info(f"ElevenLabs TTS complete: {media_url} ({os.path.getsize(filepath)} bytes)")
                return media_url
            else:
                logger.error("ElevenLabs TTS file creation failed or file too small")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None
        else:
            logger.error(f"ElevenLabs API error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"ElevenLabs TTS generation failed: {e}")
        return None

def generate_gtts_fallback(text):
    """
    Generate TTS using gTTS - optimized for speed and reliability
    """
    try:
        logger.info(f"gTTS generation for: '{text[:50]}...'")
        
        # Clean text for gTTS
        clean_text = text.strip()
        if not clean_text:
            logger.error("Empty text provided to gTTS")
            return None
            
        if len(clean_text) > 1000:
            clean_text = clean_text[:1000]
            logger.warning("Text truncated to 1000 characters for speed")
        
        # Use hash for consistent filenames (enables caching)
        text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
        filename = f"gtts_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check if file already exists (caching)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            media_url = f"/media/tts/{filename}"
            logger.info(f"Using cached gTTS: {media_url}")
            return media_url
        
        # Generate gTTS
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(filepath)
        
        # Verify file was created
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            if file_size > 100:
                media_url = f"/media/tts/{filename}"
                logger.info(f"gTTS complete: {media_url} ({file_size} bytes)")
                return media_url
            else:
                logger.warning(f"gTTS file too small: {file_size} bytes")
                if os.path.exists(filepath):
                    os.remove(filepath)
        
    except Exception as e:
        logger.error(f"gTTS failed: {type(e).__name__}: {e}")
    
    return None

def generate_tts(text, model="female_professional", force_gtts=True, force_elevenlabs=False):
    """
    Generate TTS audio using gTTS as primary with ElevenLabs as future option
    Models available: female_professional, female_friendly (currently using gTTS)
    """
    
    # Clean and validate text
    if not text or not text.strip():
        logger.error("Empty text provided for TTS")
        return None
    
    clean_text = text.strip()
    if len(clean_text) > 5000:
        clean_text = clean_text[:5000]
        logger.warning("Text truncated to 5000 characters for TTS")
    
    # Use gTTS as primary method (since ElevenLabs API key needs permissions)
    if force_gtts or not force_elevenlabs:
        logger.info("Using gTTS for female voice generation")
        return generate_gtts_fallback(clean_text)
    
    # ElevenLabs option (currently disabled due to API key permissions)
    if force_elevenlabs and ELEVENLABS_API_KEY:
        logger.info(f"Attempting ElevenLabs TTS with voice: {model}")
        logger.info(f"API Key present: {bool(ELEVENLABS_API_KEY)}")
        
        elevenlabs_result = generate_elevenlabs_tts(clean_text, model)
        
        if elevenlabs_result:
            logger.info(f"ElevenLabs TTS successful: {elevenlabs_result}")
            return elevenlabs_result
        else:
            logger.warning("ElevenLabs TTS failed, falling back to gTTS")
            return generate_gtts_fallback(clean_text)
    
    # Default fallback to gTTS
    logger.info("Using gTTS as default TTS method")
    return generate_gtts_fallback(clean_text)

def test_tts_generation(test_text=None):
    """
    Test function to debug TTS generation
    """
    if test_text is None:
        test_text = "Hello, this is a test of the text to speech system. Can you hear me clearly?"
    
    logger.info(f"Testing TTS with text: '{test_text}'")
    
    # Test primary TTS
    logger.info("Testing primary TTS...")
    result = generate_tts(test_text)
    
    if result:
        logger.info(f"TTS test successful: {result}")
        return result
    else:
        logger.error("TTS test failed")
        return None

# Alias for backwards compatibility
generate_tts_audio = generate_tts

def check_tts_system():
    """
    Basic TTS system health check
    """
    try:
        health_info = {
            'media_root': settings.MEDIA_ROOT,
            'elevenlabs_api_key': bool(ELEVENLABS_API_KEY),
            'gtts_available': True,
            'test_generation': False
        }
        
        # Test basic TTS generation
        test_result = generate_gtts_fallback("Hello world test")
        health_info['test_generation'] = bool(test_result)
        
        return health_info
    except Exception as e:
        return {'error': str(e), 'test_generation': False}

# Export main functions
__all__ = [
    'generate_tts',
    'generate_gtts_fallback',
    'generate_elevenlabs_tts',
    'test_tts_generation',
    'check_tts_system',
    'generate_tts_audio'
]