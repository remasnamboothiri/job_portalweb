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

# ElevenLabs Female Voice Configuration - Your Selected Voice
ELEVENLABS_VOICES = {
    "female_interview": {
        "voice_id": "i4CzbCVWoqvD0P1QJCUL",  # Your selected female voice for interviews
        "name": "Interview Female Voice",
        "description": "Selected female voice perfect for job interviews",
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
    logger.warning(f"API key value: '{ELEVENLABS_API_KEY}' (length: {len(ELEVENLABS_API_KEY)})")
else:
    logger.info("ElevenLabs API key configured successfully")
    logger.info(f"API key length: {len(ELEVENLABS_API_KEY)} characters")

def generate_elevenlabs_tts(text, voice="female_interview"):
    """
    Generate TTS audio using ElevenLabs API with female voice (direct API calls)
    """
    try:
        if not ELEVENLABS_API_KEY:
            logger.error("ElevenLabs API key not configured")
            return None
            
        # Validate voice
        if voice not in ELEVENLABS_VOICES:
            logger.warning(f"Invalid voice '{voice}', using 'female_interview'")
            voice = "female_interview"
        
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
            
            # Specific handling for common errors
            if response.status_code == 401:
                if "unusual_activity" in response.text:
                    logger.error("ElevenLabs account flagged for unusual activity - need new API key or paid plan")
                else:
                    logger.error("ElevenLabs API key invalid or expired")
            elif response.status_code == 429:
                logger.error("ElevenLabs rate limit exceeded")
            elif response.status_code == 422:
                logger.error("ElevenLabs request validation failed")
            
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
        
        # Generate gTTS with better settings for female voice
        tts = gTTS(text=clean_text, lang='en', slow=False, tld='com')  # Use .com for more natural voice
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

# RunPod TTS removed - using ElevenLabs only

def generate_tts(text, model="female_interview", force_gtts=False):
    """
    Generate TTS audio using ElevenLabs as primary with gTTS fallback
    Models: female_interview (Your selected ElevenLabs voice)
    """
    
    # Clean and validate text
    if not text or not text.strip():
        logger.error("Empty text provided for TTS")
        return None
    
    clean_text = text.strip()
    if len(clean_text) > 5000:
        clean_text = clean_text[:5000]
        logger.warning("Text truncated to 5000 characters for TTS")
    
    # Force gTTS if explicitly requested
    if force_gtts:
        logger.info("Force gTTS requested")
        return generate_gtts_fallback(clean_text)
    
    # RunPod/Chatterbox support removed - using ElevenLabs only
    
    # Try ElevenLabs first (primary method) - RE-ENABLED with new API key
    if ELEVENLABS_API_KEY and model in ELEVENLABS_VOICES:
        logger.info(f"Attempting ElevenLabs TTS with voice: {model}")
        elevenlabs_result = generate_elevenlabs_tts(clean_text, model)
        if elevenlabs_result:
            logger.info(f"ElevenLabs TTS successful: {elevenlabs_result}")
            return elevenlabs_result
        else:
            logger.warning("ElevenLabs TTS failed, falling back to gTTS")
    
    # Fallback to gTTS only if ElevenLabs fails
    logger.info("Using gTTS fallback")
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

# Removed backwards compatibility alias - not needed

def estimate_audio_duration(text, words_per_minute=140):
    """
    Estimate audio duration based on text length
    """
    if not text or not text.strip():
        return 2.0
    
    word_count = len(text.split())
    duration_seconds = (word_count / words_per_minute) * 60
    duration_seconds *= 1.15  # Add padding
    return max(2.0, min(duration_seconds, 30.0))

def get_audio_duration(audio_path):
    """
    Get audio duration from file
    """
    try:
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            estimated_duration = file_size / 1024
            return max(2.0, min(estimated_duration, 30.0))
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
    return None

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
        test_result = generate_tts("Hello world test")
        health_info['test_generation'] = bool(test_result)
        
        return health_info
    except Exception as e:
        return {'error': str(e), 'test_generation': False}

# Export main functions - cleaned up
__all__ = [
    'generate_tts',              # Main TTS function (ElevenLabs + gTTS fallback)
    'generate_gtts_fallback',    # Essential backup system
    'generate_elevenlabs_tts',   # Your primary ElevenLabs voice
    'test_tts_generation',       # Testing function
    'check_tts_system',          # Health check
    'estimate_audio_duration',   # Duration calculation
    'get_audio_duration'         # Audio file duration
]

# Removed unnecessary RunPod/Chatterbox functions - using ElevenLabs only