"""
CORRECTED TTS.PY - Fixed for Monika Sogam voice (EaBs7G1VibMrNAuz2Na7)
"""
import requests
import os
from gtts import gTTS
from django.conf import settings
import hashlib
import logging

# Set up logging
logger = logging.getLogger(__name__)

# ElevenLabs TTS Configuration - FIXED
ELEVENLABS_API_KEY = getattr(settings, 'ELEVENLABS_API_KEY', '') or os.environ.get('ELEVENLABS_API_KEY', '')
if ELEVENLABS_API_KEY:
    ELEVENLABS_API_KEY = ELEVENLABS_API_KEY.strip()

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# YOUR SPECIFIC VOICE ID - Monika Sogam
MONIKA_VOICE_ID = "EaBs7G1VibMrNAuz2Na7"  # Monika Sogam - Natural Conversations

# Voice configuration with your preferred voice
VOICE_OPTIONS = {
    "female_interview": {
        "voice_id": MONIKA_VOICE_ID,  # Using your specific voice
        "name": "Monika Sogam - Natural Conversations",
        "model": "eleven_multilingual_v2"
    },
    "female_natural": {
        "voice_id": MONIKA_VOICE_ID,  # All using Monika voice as requested
        "name": "Monika Sogam - Natural Conversations",
        "model": "eleven_multilingual_v2"
    },
    "female_professional": {
        "voice_id": MONIKA_VOICE_ID,  # All using Monika voice as requested
        "name": "Monika Sogam - Natural Conversations",
        "model": "eleven_multilingual_v2"
    }
}

def check_elevenlabs_status():
    """Check if ElevenLabs API is working"""
    if not ELEVENLABS_API_KEY:
        return False, "API key not configured"
    
    try:
        headers = {
            'xi-api-key': ELEVENLABS_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Test API with user endpoint
        response = requests.get(
            "https://api.elevenlabs.io/v1/user", 
            headers=headers, 
            timeout=15
        )
        
        logger.info(f"ElevenLabs API test response: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            subscription = user_data.get('subscription', {})
            tier = subscription.get('tier', 'free')
            logger.info(f"ElevenLabs account tier: {tier}")
            return True, f"API working - {tier} tier"
        elif response.status_code == 401:
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', {})
                error_msg = error_detail.get('message', 'Invalid API key')
                logger.error(f"ElevenLabs authentication error: {error_msg}")
                
                if 'unusual activity' in error_msg.lower():
                    return False, "Account flagged for unusual activity - upgrade to paid plan required"
                else:
                    return False, f"Authentication failed: {error_msg}"
            except:
                return False, "Authentication failed - invalid API key"
        elif response.status_code == 429:
            return False, "Rate limited - too many requests"
        else:
            return False, f"API error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        logger.error("ElevenLabs API timeout")
        return False, "API timeout"
    except requests.exceptions.ConnectionError:
        logger.error("ElevenLabs connection error")
        return False, "Connection error"
    except Exception as e:
        logger.error(f"ElevenLabs status check failed: {e}")
        return False, f"Unknown error: {str(e)}"

def generate_elevenlabs_tts(text, voice="female_interview"):
    """Generate TTS using ElevenLabs with Monika Sogam voice"""
    try:
        if not ELEVENLABS_API_KEY:
            logger.error("ElevenLabs API key not configured")
            return None
        
        # Use Monika voice for all requests
        voice_config = VOICE_OPTIONS[voice]
        voice_id = voice_config["voice_id"]  # This will always be Monika's ID
        model_id = voice_config["model"]
        
        logger.info(f"Using Monika Sogam voice (ID: {voice_id})")
        logger.info(f"Text to synthesize: '{text[:50]}...'")
        
        # Create filename for caching
        text_hash = hashlib.md5(f"{text}_monika_sogam".encode()).hexdigest()[:8]
        filename = f"monika_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check cache first
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            media_url = f"/media/tts/{filename}"
            logger.info(f"Using cached Monika voice TTS: {media_url}")
            return media_url
        
        # Prepare API request
        url = f"{ELEVENLABS_API_URL}/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        # Optimized settings for natural conversation voice
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.71,        # Good for natural conversations
                "similarity_boost": 0.5,  # Balanced similarity
                "style": 0.0,            # Neutral style
                "use_speaker_boost": True
            }
        }
        
        logger.info(f"Making request to ElevenLabs API: {url}")
        logger.info(f"Using model: {model_id}")
        
        # Make the API request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        logger.info(f"ElevenLabs response status: {response.status_code}")
        
        if response.status_code == 200:
            # Save the audio file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Verify file was created successfully
            if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                media_url = f"/media/tts/{filename}"
                file_size = os.path.getsize(filepath)
                logger.info(f"SUCCESS: Monika voice TTS generated: {media_url} ({file_size} bytes)")
                return media_url
            else:
                logger.error("Failed to create audio file")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None
        
        # Handle API errors
        else:
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', {})
                
                if response.status_code == 401:
                    error_msg = error_detail.get('message', 'Authentication failed')
                    logger.error(f"API key issue: {error_msg}")
                    
                    if 'unusual activity' in error_msg.lower():
                        logger.error("CRITICAL: Account flagged - upgrade to paid plan required")
                    
                elif response.status_code == 422:
                    logger.error(f"Voice ID or request invalid: {error_detail}")
                    logger.error("Check if Monika Sogam voice ID is correct and accessible")
                elif response.status_code == 429:
                    logger.error("Rate limit exceeded")
                else:
                    logger.error(f"API error {response.status_code}: {error_detail}")
                
            except:
                logger.error(f"API error {response.status_code}: {response.text}")
            
            return None
            
    except Exception as e:
        logger.error(f"ElevenLabs TTS generation failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None

def generate_gtts_fallback(text):
    """Generate audio using Google TTS as fallback"""
    try:
        logger.info(f"Using gTTS fallback for: '{text[:50]}...'")
        
        clean_text = text.strip()
        if not clean_text:
            return None
        
        if len(clean_text) > 1000:
            clean_text = clean_text[:997] + "..."
        
        # Create filename
        text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
        filename = f"gtts_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check cache
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            media_url = f"/media/tts/{filename}"
            logger.info(f"Using cached gTTS: {media_url}")
            return media_url
        
        # Generate gTTS
        tts = gTTS(text=clean_text, lang='en', slow=False, tld='com')
        tts.save(filepath)
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            media_url = f"/media/tts/{filename}"
            file_size = os.path.getsize(filepath)
            logger.info(f"gTTS fallback complete: {media_url} ({file_size} bytes)")
            return media_url
        
    except Exception as e:
        logger.error(f"gTTS fallback failed: {e}")
    
    return None

def generate_tts(text, model="female_interview"):
    """Main TTS function - tries ElevenLabs with Monika voice first"""
    if not text or not text.strip():
        return None
    
    clean_text = text.strip()
    if len(clean_text) > 5000:
        clean_text = clean_text[:4997] + "..."
    
    # Always try ElevenLabs first if API key is configured
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
        logger.info("Attempting ElevenLabs with Monika Sogam voice...")
        
        # Check API status
        api_status, api_message = check_elevenlabs_status()
        if api_status:
            logger.info(f"ElevenLabs API is working: {api_message}")
            elevenlabs_result = generate_elevenlabs_tts(clean_text, model)
            if elevenlabs_result:
                logger.info(f"SUCCESS: ElevenLabs Monika voice generated: {elevenlabs_result}")
                return elevenlabs_result
            else:
                logger.warning("ElevenLabs generation failed, falling back to gTTS")
        else:
            logger.warning(f"ElevenLabs API not available: {api_message}")
    else:
        logger.info("ElevenLabs API key not configured properly")
    
    # Fallback to gTTS
    logger.info("Using gTTS fallback")
    return generate_gtts_fallback(clean_text)

def estimate_audio_duration(text, words_per_minute=140):
    """Estimate audio duration"""
    if not text or not text.strip():
        return 3.0
    
    word_count = len(text.split())
    duration_seconds = (word_count / words_per_minute) * 60
    duration_seconds *= 1.2  # Add padding
    return max(2.0, min(duration_seconds, 30.0))

def get_audio_duration(audio_path):
    """Get actual audio duration from file"""
    try:
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            # Estimate based on file size (rough calculation for MP3)
            estimated_duration = (file_size * 8) / (128 * 1024)
            return max(2.0, min(estimated_duration, 30.0))
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
    return None

def check_tts_system():
    """Comprehensive TTS system health check"""
    try:
        health_info = {
            'timestamp': str(timezone.now() if 'timezone' in globals() else 'unknown'),
            'media_root_exists': os.path.exists(settings.MEDIA_ROOT),
            'tts_directory_exists': os.path.exists(os.path.join(settings.MEDIA_ROOT, 'tts')),
            'elevenlabs_api_key_present': bool(ELEVENLABS_API_KEY),
            'elevenlabs_api_key_length': len(ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else 0,
            'monika_voice_id': MONIKA_VOICE_ID,
            'gtts_available': True,
            'elevenlabs_status': None,
            'elevenlabs_message': None,
            'test_generation': False,
            'test_service': None
        }
        
        # Check ElevenLabs status
        if ELEVENLABS_API_KEY:
            api_status, api_message = check_elevenlabs_status()
            health_info['elevenlabs_status'] = api_status
            health_info['elevenlabs_message'] = api_message
        
        # Test generation
        logger.info("Testing TTS generation with Monika voice...")
        test_result = generate_tts("Hello, this is a test of the Monika Sogam voice.")
        health_info['test_generation'] = bool(test_result)
        
        if test_result:
            if 'monika' in test_result:
                health_info['test_service'] = 'elevenlabs_monika'
            elif 'gtts' in test_result:
                health_info['test_service'] = 'gtts_fallback'
            else:
                health_info['test_service'] = 'unknown'
        else:
            health_info['test_service'] = 'failed'
        
        logger.info("TTS Health Check Results:")
        for key, value in health_info.items():
            logger.info(f"   {key}: {value}")
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'error': str(e), 'test_generation': False}

# Export all functions
__all__ = [
    'generate_tts',
    'generate_elevenlabs_tts', 
    'generate_gtts_fallback',
    'check_tts_system',
    'check_elevenlabs_status',
    'estimate_audio_duration',
    'get_audio_duration',
    'MONIKA_VOICE_ID'
]





# """
# CORRECTED TTS.PY - The issue is your ElevenLabs API key is banned
# Replace your entire tts.py with this version
# """
# import requests
# import os
# from gtts import gTTS
# from django.conf import settings
# import hashlib
# import logging

# # Set up logging
# logger = logging.getLogger(__name__)

# # ElevenLabs TTS Configuration
# ELEVENLABS_API_KEY = settings.ELEVENLABS_API_KEY.strip() if settings.ELEVENLABS_API_KEY else None
# ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# # CORRECTED: Your voice ID has issues - use reliable female voices
# FEMALE_VOICE_OPTIONS = {
#     "female_interview": {
#         "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Professional female
#         "name": "Rachel - Professional Female",
#         "model": "eleven_multilingual_v2"
#     },
#     "female_natural": {
#         "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Sarah - Natural female
#         "name": "Sarah - Natural Female", 
#         "model": "eleven_multilingual_v2"
#     },
#     "female_professional": {
#         "voice_id": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - Professional
#         "name": "Dorothy - Professional Female",
#         "model": "eleven_multilingual_v2"
#     }
# }

# def generate_elevenlabs_tts(text, voice="female_interview"):
#     """
#     CORRECTED: Generate TTS with working voice IDs and proper error handling
#     """
#     try:
#         if not ELEVENLABS_API_KEY:
#             logger.error("ElevenLabs API key not configured")
#             return None
            
#         voice_config = FEMALE_VOICE_OPTIONS.get(voice, FEMALE_VOICE_OPTIONS["female_interview"])
#         voice_id = voice_config["voice_id"]
#         model_id = voice_config["model"]
        
#         logger.info(f"🎵 ElevenLabs TTS generation with voice ID: {voice_id}")
#         logger.info(f"📝 Text: '{text[:50]}...'")
        
#         # Create filename for caching
#         text_hash = hashlib.md5(f"{text}_elevenlabs_{voice}".encode()).hexdigest()[:8]
#         filename = f"elevenlabs_{voice}_{text_hash}.mp3"
#         tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
#         os.makedirs(tts_dir, exist_ok=True)
#         filepath = os.path.join(tts_dir, filename)
        
#         # Check if file already exists
#         if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
#             media_url = f"/media/tts/{filename}"
#             logger.info(f"📁 Using cached ElevenLabs TTS: {media_url}")
#             return media_url
        
#         # CORRECTED: Prepare API request with proper headers
#         url = f"{ELEVENLABS_API_URL}/{voice_id}"
#         headers = {
#             "Accept": "audio/mpeg",
#             "Content-Type": "application/json",
#             "xi-api-key": ELEVENLABS_API_KEY
#         }
        
#         # CORRECTED: Simplified payload to avoid issues
#         payload = {
#             "text": text,
#             "model_id": model_id,
#             "voice_settings": {
#                 "stability": 0.5,
#                 "similarity_boost": 0.8
#             }
#         }
        
#         logger.info(f"🌐 Making request to ElevenLabs API: {url}")
        
#         # Make API request with shorter timeout
#         response = requests.post(url, json=payload, headers=headers, timeout=15)
        
#         if response.status_code == 200:
#             # Save audio data
#             with open(filepath, 'wb') as f:
#                 f.write(response.content)
            
#             if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
#                 media_url = f"/media/tts/{filename}"
#                 logger.info(f"✅ ElevenLabs TTS complete: {media_url} ({os.path.getsize(filepath)} bytes)")
#                 return media_url
#             else:
#                 logger.error("❌ ElevenLabs TTS file creation failed")
#                 if os.path.exists(filepath):
#                     os.remove(filepath)
#                 return None
        
#         # CORRECTED: Handle specific API errors your logs show
#         elif response.status_code == 401:
#             logger.error("🔑 API key invalid or expired - Your ElevenLabs account has issues")
#             logger.error(f"Response: {response.text}")
#             return None
#         elif response.status_code == 429:
#             logger.error("⏰ Rate limit exceeded")
#             return None
#         elif response.status_code == 422:
#             logger.error("📝 Request validation failed")
#             logger.error(f"Response: {response.text}")
#             return None
#         else:
#             logger.error(f"❌ ElevenLabs API error: {response.status_code}")
#             logger.error(f"Response: {response.text}")
#             return None
            
#     except Exception as e:
#         logger.error(f"❌ ElevenLabs TTS generation failed: {e}")
#         return None

# def generate_gtts_fallback(text):
#     """
#     CORRECTED: Reliable gTTS fallback with proper error handling
#     """
#     try:
#         logger.info(f"🔄 gTTS fallback for: '{text[:50]}...'")
        
#         # Clean text for gTTS
#         clean_text = text.strip()
#         if not clean_text:
#             logger.error("Empty text provided to gTTS")
#             return None
            
#         if len(clean_text) > 1000:
#             clean_text = clean_text[:1000]
#             logger.warning("Text truncated to 1000 characters")
        
#         # Create filename
#         text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
#         filename = f"gtts_{text_hash}.mp3"
#         tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
#         os.makedirs(tts_dir, exist_ok=True)
#         filepath = os.path.join(tts_dir, filename)
        
#         # Check cache
#         if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
#             media_url = f"/media/tts/{filename}"
#             logger.info(f"📁 Using cached gTTS: {media_url}")
#             return media_url
        
#         # Generate gTTS
#         tts = gTTS(text=clean_text, lang='en', slow=False, tld='com')
#         tts.save(filepath)
        
#         if os.path.exists(filepath):
#             file_size = os.path.getsize(filepath)
#             if file_size > 100:
#                 media_url = f"/media/tts/{filename}"
#                 logger.info(f"✅ gTTS complete: {media_url} ({file_size} bytes)")
#                 return media_url
#             else:
#                 logger.warning(f"⚠️ gTTS file too small: {file_size} bytes")
#                 if os.path.exists(filepath):
#                     os.remove(filepath)
        
#     except Exception as e:
#         logger.error(f"❌ gTTS failed: {type(e).__name__}: {e}")
    
#     return None

# def generate_tts(text, model="female_interview"):
#     """
#     CORRECTED: Main TTS function that handles ElevenLabs API failures properly
#     """
#     if not text or not text.strip():
#         logger.error("Empty text provided for TTS")
#         return None
    
#     clean_text = text.strip()
#     if len(clean_text) > 3000:
#         clean_text = clean_text[:3000]
#         logger.warning("Text truncated to 3000 characters")
    
#     # CORRECTED: Skip ElevenLabs if API key is known to be bad
#     # Based on your logs, your API key has "unusual activity" restrictions
#     if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 10:
#         logger.info("🎤 Trying ElevenLabs first...")
#         elevenlabs_result = generate_elevenlabs_tts(clean_text, model)
#         if elevenlabs_result:
#             logger.info(f"🎉 ElevenLabs TTS successful: {elevenlabs_result}")
#             return elevenlabs_result
#         else:
#             logger.warning("⚠️ ElevenLabs failed, using gTTS fallback")
#     else:
#         logger.info("⚠️ ElevenLabs API key missing/invalid, using gTTS")
    
#     # Use gTTS fallback
#     return generate_gtts_fallback(clean_text)

# def estimate_audio_duration(text, words_per_minute=140):
#     """Calculate estimated audio duration"""
#     if not text or not text.strip():
#         return 3.0
    
#     word_count = len(text.split())
#     duration_seconds = (word_count / words_per_minute) * 60
#     duration_seconds *= 1.2  # Add padding
#     return max(3.0, min(duration_seconds, 30.0))

# def get_audio_duration(audio_path):
#     """Get duration from audio file"""
#     try:
#         if os.path.exists(audio_path):
#             file_size = os.path.getsize(audio_path)
#             # Rough estimation: MP3 bitrate ~128kbps
#             estimated_duration = (file_size * 8) / (128 * 1024)
#             return max(2.0, min(estimated_duration, 30.0))
#     except Exception as e:
#         logger.error(f"Error getting audio duration: {e}")
#     return None

# def check_tts_system():
#     """Health check for TTS system"""
#     try:
#         health_info = {
#             'media_root_exists': os.path.exists(settings.MEDIA_ROOT),
#             'elevenlabs_api_key_present': bool(ELEVENLABS_API_KEY),
#             'elevenlabs_api_key_length': len(ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else 0,
#             'gtts_available': True,
#             'test_generation': False
#         }
        
#         # Test generation
#         test_result = generate_tts("Hello, this is a test.")
#         health_info['test_generation'] = bool(test_result)
#         health_info['test_service'] = 'elevenlabs' if test_result and 'elevenlabs' in test_result else 'gtts' if test_result else 'failed'
        
#         logger.info("🏥 TTS Health Check Results:")
#         for key, value in health_info.items():
#             logger.info(f"   {key}: {value}")
        
#         return health_info
#     except Exception as e:
#         return {'error': str(e), 'test_generation': False}

# # Export functions
# __all__ = [
#     'generate_tts',
#     'generate_elevenlabs_tts', 
#     'generate_gtts_fallback',
#     'check_tts_system',
#     'estimate_audio_duration',
#     'get_audio_duration'
# ]