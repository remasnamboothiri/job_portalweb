"""
FIXED TTS.PY - Improved ElevenLabs integration with better error handling
"""
import requests
import os
from gtts import gTTS
from django.conf import settings
import hashlib
import logging
from django.utils import timezone
from mutagen.mp3 import MP3
import time

# Set up logging
logger = logging.getLogger(__name__)

# ElevenLabs TTS Configuration
VOICE_ID = "EaBs7G1VibMrNAuz2Na7"
ELEVENLABS_API_KEY = getattr(settings, 'ELEVENLABS_API_KEY', '') or os.environ.get('ELEVENLABS_API_KEY', '')
if ELEVENLABS_API_KEY:
    ELEVENLABS_API_KEY = ELEVENLABS_API_KEY.strip()

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# Updated Voice Configuration - Using stable voice IDs
VOICE_OPTIONS = {
    "female_interview": {
        "voice_id": "EaBs7G1VibMrNAuz2Na7",  # monica - professional natural voice 
        "name": "Monika Sogam - Natural Conversations",
        "model": "eleven_multilingual_v2"
    }

    # "female_natural": {
    #     "voice_id": "EaBs7G1VibMrNAuz2Na7",  # Domi - Natural, warm voice
    #     "name": "Domi - Natural Conversation Voice",
    #     "model": "eleven_multilingual_v2"
    # },
    # "female_professional": {
    #     "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella - Professional, friendly
    #     "name": "Bella - Professional Voice",
    #     "model": "eleven_multilingual_v2"
    # }
}

def check_elevenlabs_status():
    """Check if ElevenLabs API is working with better error detection"""
    if not ELEVENLABS_API_KEY:
        return False, "API key not configured"
    
    if len(ELEVENLABS_API_KEY) < 20:
        return False, "API key too short - check configuration"
    
    try:
        headers = {
            'xi-api-key': ELEVENLABS_API_KEY,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Test with user endpoint first
        logger.info("Testing ElevenLabs API connection...")
        response = requests.get(
            "https://api.elevenlabs.io/v1/user", 
            headers=headers, 
            timeout=10
        )
        
        logger.info(f"ElevenLabs API response: {response.status_code}")
        
        if response.status_code == 200:
            try:
                user_data = response.json()
                subscription = user_data.get('subscription', {})
                tier = subscription.get('tier', 'free')
                character_count = user_data.get('character_count', 0)
                character_limit = user_data.get('character_limit', 0)
                
                logger.info(f"ElevenLabs account - Tier: {tier}, Characters: {character_count}/{character_limit}")
                
                if tier == 'free' and character_count >= character_limit:
                    return False, f"Free tier limit exceeded ({character_count}/{character_limit})"
                
                return True, f"API working - {tier} tier ({character_count}/{character_limit} characters used)"
                
            except Exception as e:
                logger.error(f"Failed to parse user data: {e}")
                return True, "API working but couldn't get account details"
        
        elif response.status_code == 401:
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', {})
                error_msg = error_detail.get('message', 'Authentication failed')
                
                logger.error(f"ElevenLabs authentication error: {error_msg}")
                
                if 'unusual activity' in error_msg.lower():
                    return False, "Account suspended for unusual activity - contact ElevenLabs support"
                elif 'invalid' in error_msg.lower():
                    return False, "Invalid API key - please check your ElevenLabs dashboard"
                else:
                    return False, f"Authentication failed: {error_msg}"
                    
            except:
                return False, "Authentication failed - invalid API key format"
        
        elif response.status_code == 429:
            return False, "Rate limit exceeded - please wait before trying again"
        
        elif response.status_code >= 500:
            return False, f"ElevenLabs server error ({response.status_code}) - try again later"
        
        else:
            return False, f"API error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        logger.error("ElevenLabs API timeout")
        return False, "API request timed out"
    except requests.exceptions.ConnectionError:
        logger.error("ElevenLabs connection error") 
        return False, "Cannot connect to ElevenLabs servers"
    except Exception as e:
        logger.error(f"ElevenLabs status check failed: {e}")
        return False, f"Connection error: {str(e)[:100]}"

def generate_elevenlabs_tts(text, voice="female_interview"):
    """Generate TTS using ElevenLabs with improved error handling"""
    try:
        if not ELEVENLABS_API_KEY:
            logger.warning("ElevenLabs API key not configured - using fallback")
            return None
        
        # Get voice configuration
        if voice not in VOICE_OPTIONS:
            voice = "female_interview"
        
        voice_config = VOICE_OPTIONS[voice]
        voice_id = voice_config["voice_id"]
        model_id = voice_config["model"]
        voice_name = voice_config["name"]
        
        logger.info(f"Generating TTS with {voice_name} (ID: {voice_id})")
        
        # Clean and validate text
        clean_text = text.strip()
        if len(clean_text) > 2000:  # ElevenLabs character limit for some tiers
            clean_text = clean_text[:1997] + "..."
        
        # Create filename for caching
        text_hash = hashlib.md5(f"{clean_text}_{voice_id}".encode()).hexdigest()[:8]
        filename = f"elevenlabs_{voice}_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check cache first
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
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
        
        # Optimized voice settings for interview
        payload = {
            "text": clean_text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.75,           # More stable for professional voice
                "similarity_boost": 0.75,    # Maintain voice characteristics
                "style": 0.0,               # Neutral style
                "use_speaker_boost": True    # Enhanced clarity
            }
        }
        
        logger.info(f"Making ElevenLabs API request to: {url}")
        
        # Make the API request with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=25)
                
                logger.info(f"ElevenLabs response: {response.status_code} (attempt {attempt + 1})")
                
                if response.status_code == 200:
                    # Save the audio file
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    # Verify file was created successfully
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                        media_url = f"/media/tts/{filename}"
                        file_size = os.path.getsize(filepath)
                        logger.info(f"SUCCESS: ElevenLabs TTS generated: {media_url} ({file_size} bytes)")
                        return media_url
                    else:
                        logger.error("Generated audio file is too small or corrupted")
                        if os.path.exists(filepath):
                            os.remove(filepath)
                
                # Handle specific error cases
                elif response.status_code == 401:
                    logger.error("ElevenLabs authentication failed - API key issue")
                    break  # Don't retry auth errors
                
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        logger.warning("Rate limited, retrying in 2 seconds...")
                        time.sleep(2)
                        continue
                    else:
                        logger.error("Rate limit exceeded after retries")
                        break
                
                elif response.status_code == 422:
                    try:
                        error_data = response.json()
                        logger.error(f"Invalid request: {error_data}")
                    except:
                        logger.error(f"Invalid request: {response.text}")
                    break  # Don't retry validation errors
                
                else:
                    logger.error(f"ElevenLabs API error {response.status_code}: {response.text[:200]}")
                    if attempt == max_retries - 1:
                        break
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    logger.error("Final timeout - giving up")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                break
        
        return None
        
    except Exception as e:
        logger.error(f"ElevenLabs TTS generation failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None

def generate_gtts_fallback(text):
    """Improved Google TTS fallback with better error handling"""
    try:
        logger.info(f"Using gTTS fallback for: '{text[:50]}...'")
        
        clean_text = text.strip()
        if not clean_text:
            logger.error("Empty text provided to gTTS")
            return None
        
        # gTTS has a character limit
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
        
        # Generate gTTS with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating gTTS (attempt {attempt + 1})...")
                tts = gTTS(text=clean_text, lang='en', slow=False, tld='com')
                tts.save(filepath)
                
                # Verify file
                if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                    media_url = f"/media/tts/{filename}"
                    file_size = os.path.getsize(filepath)
                    logger.info(f"gTTS success: {media_url} ({file_size} bytes)")
                    return media_url
                else:
                    logger.warning(f"gTTS generated empty/small file (attempt {attempt + 1})")
                    if os.path.exists(filepath):
                        os.remove(filepath)
                
            except Exception as e:
                logger.warning(f"gTTS attempt {attempt + 1} failed: {e}")
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass
                
                if attempt == max_retries - 1:
                    logger.error("All gTTS attempts failed")
                    return None
                
                # Wait before retry
                import time
                time.sleep(1)
        
        return None
        
    except Exception as e:
        logger.error(f"gTTS fallback completely failed: {e}")
        return None

def generate_tts(text, model="female_interview"):
    """Main TTS function with intelligent fallback"""
    if not text or not text.strip():
        logger.error("Empty text provided to generate_tts")
        return None
    
    clean_text = text.strip()
    if len(clean_text) > 3000:
        clean_text = clean_text[:2997] + "..."
    
    logger.info(f"TTS requested for: '{clean_text[:50]}...' with model: {model}")
    
    # Try ElevenLabs first if properly configured
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
        logger.info("Attempting ElevenLabs TTS...")
        
        # Quick API status check
        api_status, api_message = check_elevenlabs_status()
        if api_status:
            logger.info(f"ElevenLabs API available: {api_message}")
            elevenlabs_result = generate_elevenlabs_tts(clean_text, model)
            if elevenlabs_result:
                logger.info(f"SUCCESS: ElevenLabs generated: {elevenlabs_result}")
                return elevenlabs_result
            else:
                logger.warning("ElevenLabs generation failed, using fallback")
        else:
            logger.warning(f"ElevenLabs not available: {api_message}")
            logger.info("Using gTTS fallback due to ElevenLabs issues")
    else:
        logger.info("ElevenLabs API key not configured properly, using gTTS")
        logger.info("Using gTTS fallback due to ElevenLabs issues")
    
    # Fallback to gTTS
    fallback_result = generate_gtts_fallback(clean_text)
    if fallback_result:
        logger.info(f"Fallback successful: {fallback_result}")
        return fallback_result
    else:
        logger.error("Both ElevenLabs and gTTS failed")
        return None

def estimate_audio_duration(text, words_per_minute=150):
    """Estimate audio duration based on text length"""
    if not text or not text.strip():
        return 3.0
    
    word_count = len(text.split())
    # Base calculation
    duration_seconds = (word_count / words_per_minute) * 60
    # Add padding for natural speech patterns
    duration_seconds *= 1.15
    # Ensure reasonable bounds
    return max(2.0, min(duration_seconds, 25.0))

def get_audio_duration(audio_path):
    """Get actual audio duration from file"""
    try:
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None
        
        file_size = os.path.getsize(audio_path)
        if file_size < 100:
            logger.error(f"Audio file too small: {file_size} bytes")
            return None
        
        # Try to get duration using mutagen if available
        try:
            from mutagen.mp3 import MP3
            audio = MP3(audio_path)
            duration = audio.info.length
            logger.info(f"Actual audio duration (mutagen): {duration:.2f}s")
            return duration
        except ImportError:
            logger.info("Mutagen not available, estimating duration")
        except Exception as e:
            logger.warning(f"Mutagen duration detection failed: {e}")
        
        # Fallback: estimate based on file size (rough calculation for MP3)
        # Assuming 128kbps MP3 encoding
        estimated_duration = (file_size * 8) / (128 * 1024)
        estimated_duration = max(2.0, min(estimated_duration, 25.0))
        logger.info(f"Estimated audio duration: {estimated_duration:.2f}s")
        return estimated_duration
        
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return None

def check_tts_system():
    """Comprehensive TTS system health check"""
    try:
        import time
        start_time = time.time()
        
        health_info = {
            'timestamp': timezone.now().isoformat(),
            'media_root_exists': os.path.exists(settings.MEDIA_ROOT),
            'tts_directory_exists': os.path.exists(os.path.join(settings.MEDIA_ROOT, 'tts')),
            'tts_directory_writable': os.access(os.path.join(settings.MEDIA_ROOT, 'tts'), os.W_OK),
            'elevenlabs_api_key_present': bool(ELEVENLABS_API_KEY),
            'elevenlabs_api_key_length': len(ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else 0,
            'elevenlabs_api_key_valid_format': len(ELEVENLABS_API_KEY) > 20 if ELEVENLABS_API_KEY else False,
            'available_voices': list(VOICE_OPTIONS.keys()),
            'gtts_available': True,
            'elevenlabs_status': None,
            'elevenlabs_message': None,
            'test_generation': False,
            'test_service': None,
            'test_duration': None
        }
        
        # Create TTS directory if it doesn't exist
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        try:
            os.makedirs(tts_dir, exist_ok=True)
            health_info['tts_directory_created'] = True
        except Exception as e:
            health_info['tts_directory_created'] = False
            health_info['tts_directory_error'] = str(e)
        
        # Check ElevenLabs status
        if ELEVENLABS_API_KEY:
            api_status, api_message = check_elevenlabs_status()
            health_info['elevenlabs_status'] = api_status
            health_info['elevenlabs_message'] = api_message
        
        # Test generation
        test_text = "Hello, this is a system health check for the AI interview TTS system."
        logger.info(f"Testing TTS generation with text: '{test_text}'")
        
        test_start = time.time()
        test_result = generate_tts(test_text, "female_interview")
        test_end = time.time()
        
        health_info['test_generation'] = bool(test_result)
        health_info['test_duration'] = round(test_end - test_start, 2)
        
        if test_result:
            if 'elevenlabs' in test_result:
                health_info['test_service'] = 'elevenlabs'
            elif 'gtts' in test_result:
                health_info['test_service'] = 'gtts_fallback'
            else:
                health_info['test_service'] = 'unknown'
            
            # Check if file actually exists and has reasonable size
            test_file_path = os.path.join(settings.BASE_DIR, test_result.lstrip('/'))
            if os.path.exists(test_file_path):
                health_info['test_file_size'] = os.path.getsize(test_file_path)
                health_info['test_file_exists'] = True
            else:
                health_info['test_file_exists'] = False
        else:
            health_info['test_service'] = 'failed'
        
        health_info['total_check_duration'] = round(time.time() - start_time, 2)
        
        # Log results
        logger.info("=== TTS SYSTEM HEALTH CHECK RESULTS ===")
        for key, value in health_info.items():
            logger.info(f"   {key}: {value}")
        logger.info("=====================================")
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        import traceback
        logger.error(f"Health check traceback: {traceback.format_exc()}")
        return {
            'error': str(e), 
            'test_generation': False,
            'timestamp': timezone.now().isoformat()
        }

# Clean up old TTS files periodically
def cleanup_old_tts_files(max_age_hours=24):
    """Clean up old TTS files to save disk space"""
    try:
        import time
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        if not os.path.exists(tts_dir):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        removed_count = 0
        
        for filename in os.listdir(tts_dir):
            filepath = os.path.join(tts_dir, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        removed_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove old TTS file {filename}: {e}")
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old TTS files")
        
    except Exception as e:
        logger.error(f"TTS cleanup failed: {e}")

# Export all functions
__all__ = [
    'generate_tts',
    'generate_elevenlabs_tts', 
    'generate_gtts_fallback',
    'check_tts_system',
    'check_elevenlabs_status',
    'estimate_audio_duration',
    'get_audio_duration',
    'cleanup_old_tts_files',
    'VOICE_OPTIONS'
]



#this is most tts.py 
# """
# CORRECTED TTS.PY - Fixed for Monika Sogam voice (EaBs7G1VibMrNAuz2Na7)
# """
# import requests
# import os
# from gtts import gTTS
# from django.conf import settings
# import hashlib
# import logging

# # Set up logging
# logger = logging.getLogger(__name__)

# # ElevenLabs TTS Configuration - FIXED
# ELEVENLABS_API_KEY = getattr(settings, 'ELEVENLABS_API_KEY', '') or os.environ.get('ELEVENLABS_API_KEY', '')
# if ELEVENLABS_API_KEY:
#     ELEVENLABS_API_KEY = ELEVENLABS_API_KEY.strip()

# ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# # YOUR SPECIFIC VOICE ID - Monika Sogam
# MONIKA_VOICE_ID = "EaBs7G1VibMrNAuz2Na7"  # Monika Sogam - Natural Conversations

# # Voice configuration with your preferred voice
# VOICE_OPTIONS = {
#     "female_interview": {
#         "voice_id": MONIKA_VOICE_ID,  # Using your specific voice
#         "name": "Monika Sogam - Natural Conversations",
#         "model": "eleven_multilingual_v2"
#     },
#     "female_natural": {
#         "voice_id": MONIKA_VOICE_ID,  # All using Monika voice as requested
#         "name": "Monika Sogam - Natural Conversations",
#         "model": "eleven_multilingual_v2"
#     },
#     "female_professional": {
#         "voice_id": MONIKA_VOICE_ID,  # All using Monika voice as requested
#         "name": "Monika Sogam - Natural Conversations",
#         "model": "eleven_multilingual_v2"
#     }
# }

# def check_elevenlabs_status():
#     """Check if ElevenLabs API is working"""
#     if not ELEVENLABS_API_KEY:
#         return False, "API key not configured"
    
#     try:
#         headers = {
#             'xi-api-key': ELEVENLABS_API_KEY,
#             'Content-Type': 'application/json'
#         }
        
#         # Test API with user endpoint
#         response = requests.get(
#             "https://api.elevenlabs.io/v1/user", 
#             headers=headers, 
#             timeout=15
#         )
        
#         logger.info(f"ElevenLabs API test response: {response.status_code}")
        
#         if response.status_code == 200:
#             user_data = response.json()
#             subscription = user_data.get('subscription', {})
#             tier = subscription.get('tier', 'free')
#             logger.info(f"ElevenLabs account tier: {tier}")
#             return True, f"API working - {tier} tier"
#         elif response.status_code == 401:
#             try:
#                 error_data = response.json()
#                 error_detail = error_data.get('detail', {})
#                 error_msg = error_detail.get('message', 'Invalid API key')
#                 logger.error(f"ElevenLabs authentication error: {error_msg}")
                
#                 if 'unusual activity' in error_msg.lower():
#                     return False, "Account flagged for unusual activity - upgrade to paid plan required"
#                 else:
#                     return False, f"Authentication failed: {error_msg}"
#             except:
#                 return False, "Authentication failed - invalid API key"
#         elif response.status_code == 429:
#             return False, "Rate limited - too many requests"
#         else:
#             return False, f"API error: {response.status_code}"
            
#     except requests.exceptions.Timeout:
#         logger.error("ElevenLabs API timeout")
#         return False, "API timeout"
#     except requests.exceptions.ConnectionError:
#         logger.error("ElevenLabs connection error")
#         return False, "Connection error"
#     except Exception as e:
#         logger.error(f"ElevenLabs status check failed: {e}")
#         return False, f"Unknown error: {str(e)}"

# def generate_elevenlabs_tts(text, voice="female_interview"):
#     """Generate TTS using ElevenLabs with Monika Sogam voice"""
#     try:
#         if not ELEVENLABS_API_KEY:
#             logger.error("ElevenLabs API key not configured")
#             return None
        
#         # Use Monika voice for all requests
#         voice_config = VOICE_OPTIONS[voice]
#         voice_id = voice_config["voice_id"]  # This will always be Monika's ID
#         model_id = voice_config["model"]
        
#         logger.info(f"Using Monika Sogam voice (ID: {voice_id})")
#         logger.info(f"Text to synthesize: '{text[:50]}...'")
        
#         # Create filename for caching
#         text_hash = hashlib.md5(f"{text}_monika_sogam".encode()).hexdigest()[:8]
#         filename = f"monika_{text_hash}.mp3"
#         tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
#         os.makedirs(tts_dir, exist_ok=True)
#         filepath = os.path.join(tts_dir, filename)
        
#         # Check cache first
#         if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
#             media_url = f"/media/tts/{filename}"
#             logger.info(f"Using cached Monika voice TTS: {media_url}")
#             return media_url
        
#         # Prepare API request
#         url = f"{ELEVENLABS_API_URL}/{voice_id}"
#         headers = {
#             "Accept": "audio/mpeg",
#             "Content-Type": "application/json",
#             "xi-api-key": ELEVENLABS_API_KEY
#         }
        
#         # Optimized settings for natural conversation voice
#         payload = {
#             "text": text,
#             "model_id": model_id,
#             "voice_settings": {
#                 "stability": 0.71,        # Good for natural conversations
#                 "similarity_boost": 0.5,  # Balanced similarity
#                 "style": 0.0,            # Neutral style
#                 "use_speaker_boost": True
#             }
#         }
        
#         logger.info(f"Making request to ElevenLabs API: {url}")
#         logger.info(f"Using model: {model_id}")
        
#         # Make the API request
#         response = requests.post(url, json=payload, headers=headers, timeout=30)
        
#         logger.info(f"ElevenLabs response status: {response.status_code}")
        
#         if response.status_code == 200:
#             # Save the audio file
#             with open(filepath, 'wb') as f:
#                 f.write(response.content)
            
#             # Verify file was created successfully
#             if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
#                 media_url = f"/media/tts/{filename}"
#                 file_size = os.path.getsize(filepath)
#                 logger.info(f"SUCCESS: Monika voice TTS generated: {media_url} ({file_size} bytes)")
#                 return media_url
#             else:
#                 logger.error("Failed to create audio file")
#                 if os.path.exists(filepath):
#                     os.remove(filepath)
#                 return None
        
#         # Handle API errors
#         else:
#             try:
#                 error_data = response.json()
#                 error_detail = error_data.get('detail', {})
                
#                 if response.status_code == 401:
#                     error_msg = error_detail.get('message', 'Authentication failed')
#                     logger.error(f"API key issue: {error_msg}")
                    
#                     if 'unusual activity' in error_msg.lower():
#                         logger.error("CRITICAL: Account flagged - upgrade to paid plan required")
                    
#                 elif response.status_code == 422:
#                     logger.error(f"Voice ID or request invalid: {error_detail}")
#                     logger.error("Check if Monika Sogam voice ID is correct and accessible")
#                 elif response.status_code == 429:
#                     logger.error("Rate limit exceeded")
#                 else:
#                     logger.error(f"API error {response.status_code}: {error_detail}")
                
#             except:
#                 logger.error(f"API error {response.status_code}: {response.text}")
            
#             return None
            
#     except Exception as e:
#         logger.error(f"ElevenLabs TTS generation failed: {e}")
#         import traceback
#         logger.error(f"Full traceback: {traceback.format_exc()}")
#         return None

# def generate_gtts_fallback(text):
#     """Generate audio using Google TTS as fallback"""
#     try:
#         logger.info(f"Using gTTS fallback for: '{text[:50]}...'")
        
#         clean_text = text.strip()
#         if not clean_text:
#             return None
        
#         if len(clean_text) > 1000:
#             clean_text = clean_text[:997] + "..."
        
#         # Create filename
#         text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
#         filename = f"gtts_{text_hash}.mp3"
#         tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
#         os.makedirs(tts_dir, exist_ok=True)
#         filepath = os.path.join(tts_dir, filename)
        
#         # Check cache
#         if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
#             media_url = f"/media/tts/{filename}"
#             logger.info(f"Using cached gTTS: {media_url}")
#             return media_url
        
#         # Generate gTTS
#         tts = gTTS(text=clean_text, lang='en', slow=False, tld='com')
#         tts.save(filepath)
        
#         if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
#             media_url = f"/media/tts/{filename}"
#             file_size = os.path.getsize(filepath)
#             logger.info(f"gTTS fallback complete: {media_url} ({file_size} bytes)")
#             return media_url
        
#     except Exception as e:
#         logger.error(f"gTTS fallback failed: {e}")
    
#     return None

# def generate_tts(text, model="female_interview"):
#     """Main TTS function - tries ElevenLabs with Monika voice first"""
#     if not text or not text.strip():
#         return None
    
#     clean_text = text.strip()
#     if len(clean_text) > 5000:
#         clean_text = clean_text[:4997] + "..."
    
#     # Always try ElevenLabs first if API key is configured
#     if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
#         logger.info("Attempting ElevenLabs with Monika Sogam voice...")
        
#         # Check API status
#         api_status, api_message = check_elevenlabs_status()
#         if api_status:
#             logger.info(f"ElevenLabs API is working: {api_message}")
#             elevenlabs_result = generate_elevenlabs_tts(clean_text, model)
#             if elevenlabs_result:
#                 logger.info(f"SUCCESS: ElevenLabs Monika voice generated: {elevenlabs_result}")
#                 return elevenlabs_result
#             else:
#                 logger.warning("ElevenLabs generation failed, falling back to gTTS")
#         else:
#             logger.warning(f"ElevenLabs API not available: {api_message}")
#     else:
#         logger.info("ElevenLabs API key not configured properly")
    
#     # Fallback to gTTS
#     logger.info("Using gTTS fallback")
#     return generate_gtts_fallback(clean_text)

# def estimate_audio_duration(text, words_per_minute=140):
#     """Estimate audio duration"""
#     if not text or not text.strip():
#         return 3.0
    
#     word_count = len(text.split())
#     duration_seconds = (word_count / words_per_minute) * 60
#     duration_seconds *= 1.2  # Add padding
#     return max(2.0, min(duration_seconds, 30.0))

# def get_audio_duration(audio_path):
#     """Get actual audio duration from file"""
#     try:
#         if os.path.exists(audio_path):
#             file_size = os.path.getsize(audio_path)
#             # Estimate based on file size (rough calculation for MP3)
#             estimated_duration = (file_size * 8) / (128 * 1024)
#             return max(2.0, min(estimated_duration, 30.0))
#     except Exception as e:
#         logger.error(f"Error getting audio duration: {e}")
#     return None

# def check_tts_system():
#     """Comprehensive TTS system health check"""
#     try:
#         health_info = {
#             'timestamp': str(timezone.now() if 'timezone' in globals() else 'unknown'),
#             'media_root_exists': os.path.exists(settings.MEDIA_ROOT),
#             'tts_directory_exists': os.path.exists(os.path.join(settings.MEDIA_ROOT, 'tts')),
#             'elevenlabs_api_key_present': bool(ELEVENLABS_API_KEY),
#             'elevenlabs_api_key_length': len(ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else 0,
#             'monika_voice_id': MONIKA_VOICE_ID,
#             'gtts_available': True,
#             'elevenlabs_status': None,
#             'elevenlabs_message': None,
#             'test_generation': False,
#             'test_service': None
#         }
        
#         # Check ElevenLabs status
#         if ELEVENLABS_API_KEY:
#             api_status, api_message = check_elevenlabs_status()
#             health_info['elevenlabs_status'] = api_status
#             health_info['elevenlabs_message'] = api_message
        
#         # Test generation
#         logger.info("Testing TTS generation with Monika voice...")
#         test_result = generate_tts("Hello, this is a test of the Monika Sogam voice.")
#         health_info['test_generation'] = bool(test_result)
        
#         if test_result:
#             if 'monika' in test_result:
#                 health_info['test_service'] = 'elevenlabs_monika'
#             elif 'gtts' in test_result:
#                 health_info['test_service'] = 'gtts_fallback'
#             else:
#                 health_info['test_service'] = 'unknown'
#         else:
#             health_info['test_service'] = 'failed'
        
#         logger.info("TTS Health Check Results:")
#         for key, value in health_info.items():
#             logger.info(f"   {key}: {value}")
        
#         return health_info
        
#     except Exception as e:
#         logger.error(f"Health check failed: {e}")
#         return {'error': str(e), 'test_generation': False}

# # Export all functions
# __all__ = [
#     'generate_tts',
#     'generate_elevenlabs_tts', 
#     'generate_gtts_fallback',
#     'check_tts_system',
#     'check_elevenlabs_status',
#     'estimate_audio_duration',
#     'get_audio_duration',
#     'MONIKA_VOICE_ID'
# ]





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