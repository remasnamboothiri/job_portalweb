import requests
import os
from gtts import gTTS
from django.conf import settings
import hashlib
import logging

# Set up logging
logger = logging.getLogger(__name__)

# ElevenLabs TTS Configuration - YOUR SPECIFIC SETTINGS
ELEVENLABS_API_KEY = settings.ELEVENLABS_API_KEY.strip() if settings.ELEVENLABS_API_KEY else None
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# YOUR SPECIFIC FEMALE VOICE CONFIGURATION
FEMALE_VOICE_ID = "EaBs7G1VibMrNAuz2Na7"  # Your selected female voice

ELEVENLABS_VOICES = {
    "female_interview": {
        "voice_id": FEMALE_VOICE_ID,  # Your specific voice ID
        "name": "Selected Female Interview Voice",
        "description": "Your chosen female voice for interviews",
        "type": "elevenlabs",
        "model": "eleven_multilingual_v2"
    }
}

# Validate API key
if ELEVENLABS_API_KEY:
    logger.info("✅ ElevenLabs API key configured successfully")
    logger.info(f"🎤 Using female voice ID: {FEMALE_VOICE_ID}")
else:
    logger.error("❌ ElevenLabs API key not found")

def generate_elevenlabs_tts(text, voice="female_interview"):
    """
    Generate TTS audio using ElevenLabs API with your specific female voice
    """
    try:
        if not ELEVENLABS_API_KEY:
            logger.error("ElevenLabs API key not configured")
            return None
            
        voice_config = ELEVENLABS_VOICES[voice]
        voice_id = voice_config["voice_id"]
        model_id = voice_config["model"]
        
        logger.info(f"🎵 ElevenLabs TTS generation with voice ID: {voice_id}")
        logger.info(f"📝 Text: '{text[:50]}...'")
        
        # Create filename for caching
        text_hash = hashlib.md5(f"{text}_elevenlabs_{voice}".encode()).hexdigest()[:8]
        filename = f"elevenlabs_{voice}_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check if file already exists (caching)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            media_url = f"/media/tts/{filename}"
            logger.info(f"📁 Using cached ElevenLabs TTS: {media_url}")
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
        
        logger.info(f"🌐 Making request to ElevenLabs API: {url}")
        
        # Make API request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Save audio data directly
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Verify file was created and has content
            if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                media_url = f"/media/tts/{filename}"
                logger.info(f"✅ ElevenLabs TTS complete: {media_url} ({os.path.getsize(filepath)} bytes)")
                return media_url
            else:
                logger.error("❌ ElevenLabs TTS file creation failed or file too small")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None
        else:
            logger.error(f"❌ ElevenLabs API error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            
            # Specific error handling
            if response.status_code == 401:
                logger.error("🔑 API key invalid or expired")
            elif response.status_code == 429:
                logger.error("⏰ Rate limit exceeded")
            elif response.status_code == 422:
                logger.error("📝 Request validation failed")
            
            return None
            
    except Exception as e:
        logger.error(f"❌ ElevenLabs TTS generation failed: {e}")
        return None

def generate_gtts_fallback(text):
    """
    Generate TTS using gTTS - fallback only
    """
    try:
        logger.info(f"🔄 gTTS fallback for: '{text[:50]}...'")
        
        # Clean text for gTTS
        clean_text = text.strip()
        if not clean_text:
            logger.error("Empty text provided to gTTS")
            return None
            
        if len(clean_text) > 1000:
            clean_text = clean_text[:1000]
            logger.warning("Text truncated to 1000 characters")
        
        # Use hash for consistent filenames (enables caching)
        text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
        filename = f"gtts_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check if file already exists (caching)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            media_url = f"/media/tts/{filename}"
            logger.info(f"📁 Using cached gTTS: {media_url}")
            return media_url
        
        # Generate gTTS with better settings for female voice
        tts = gTTS(text=clean_text, lang='en', slow=False, tld='com')
        tts.save(filepath)
        
        # Verify file was created
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            if file_size > 100:
                media_url = f"/media/tts/{filename}"
                logger.info(f"✅ gTTS complete: {media_url} ({file_size} bytes)")
                return media_url
            else:
                logger.warning(f"⚠️ gTTS file too small: {file_size} bytes")
                if os.path.exists(filepath):
                    os.remove(filepath)
        
    except Exception as e:
        logger.error(f"❌ gTTS failed: {type(e).__name__}: {e}")
    
    return None

def generate_tts(text, model="female_interview"):
    """
    Generate TTS audio using ElevenLabs as PRIMARY method with gTTS fallback
    This will use YOUR specific voice: EaBs7G1VibMrNAuz2Na7
    """
    
    # Clean and validate text
    if not text or not text.strip():
        logger.error("Empty text provided for TTS")
        return None
    
    clean_text = text.strip()
    if len(clean_text) > 5000:
        clean_text = clean_text[:5000]
        logger.warning("Text truncated to 5000 characters for TTS")
    
    # 🎯 PRIMARY: Try ElevenLabs with YOUR voice ID first
    logger.info(f"🎤 Using ElevenLabs with YOUR voice ID: {FEMALE_VOICE_ID}")
    elevenlabs_result = generate_elevenlabs_tts(clean_text, model)
    if elevenlabs_result:
        logger.info(f"🎉 ElevenLabs TTS successful: {elevenlabs_result}")
        return elevenlabs_result
    else:
        logger.warning("⚠️ ElevenLabs TTS failed, falling back to gTTS")
    
    # 🔄 FALLBACK: Use gTTS only if ElevenLabs fails
    logger.info("Using gTTS fallback")
    return generate_gtts_fallback(clean_text)

def test_tts_generation(test_text=None):
    """
    Test function to verify YOUR ElevenLabs voice is working
    """
    if test_text is None:
        test_text = "Hello, this is a test of your ElevenLabs female voice for the interview system."
    
    logger.info(f"🧪 Testing TTS with YOUR voice ID: {FEMALE_VOICE_ID}")
    logger.info(f"📝 Test text: '{test_text}'")
    
    # Test ElevenLabs directly
    result = generate_tts(test_text)
    
    if result and "elevenlabs" in result:
        logger.info(f"✅ ElevenLabs test successful: {result}")
        return result
    elif result and "gtts" in result:
        logger.warning(f"⚠️ Fell back to gTTS: {result}")
        return result
    else:
        logger.error("❌ TTS test failed completely")
        return None

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
    Health check for YOUR ElevenLabs setup
    """
    try:
        health_info = {
            'media_root': settings.MEDIA_ROOT,
            'elevenlabs_api_key': bool(ELEVENLABS_API_KEY),
            'female_voice_id': FEMALE_VOICE_ID,
            'gtts_available': True,
            'test_generation': False
        }
        
        # Test YOUR ElevenLabs voice
        test_result = generate_tts("Hello world test")
        health_info['test_generation'] = bool(test_result)
        health_info['used_elevenlabs'] = test_result and "elevenlabs" in test_result if test_result else False
        
        logger.info("🏥 TTS Health Check Results:")
        for key, value in health_info.items():
            logger.info(f"   {key}: {value}")
        
        return health_info
    except Exception as e:
        return {'error': str(e), 'test_generation': False}

# Export main functions
__all__ = [
    'generate_tts',              # Main TTS function (ElevenLabs PRIMARY)
    'generate_elevenlabs_tts',   # Your specific ElevenLabs voice
    'generate_gtts_fallback',    # Fallback only
    'test_tts_generation',       # Test your voice
    'check_tts_system',          # Health check
    'estimate_audio_duration',   # Duration calculation
    'get_audio_duration'         # Audio file duration
]