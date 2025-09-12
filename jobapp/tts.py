import requests
import os
from gtts import gTTS
from django.conf import settings
import uuid
import tempfile
import time
import logging
import hashlib
import json

# Set up logging
logger = logging.getLogger(__name__)

# RunPod TTS Configuration - Using Kokkoro endpoint with chatterbox model
RUNPOD_API_KEY = getattr(settings, 'RUNPOD_API_KEY', '')
JWT_SECRET = getattr(settings, 'JWT_SECRET', '')
RUNPOD_ENDPOINT = "https://api.runpod.ai/v2/p3eso571qdfug9/runsync"

# Built-in voices configuration for chatterbox model
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

# Available voice models - Updated to use chatterbox with female_default
AVAILABLE_VOICES = {
    "chatterbox": {
        "voice_id": "female_default",  # Use female_default voice in chatterbox model
        "name": "Chatterbox Female",
        "description": "Professional female voice using chatterbox model",
        "type": "chatterbox",
        "model": "chatterbox"
    },
    "female_default": {
        "voice_id": "female_default",
        "name": "Female Default",
        "description": "Professional female voice",
        "type": "builtin",
        "model": "chatterbox"
    }
}

# Backwards compatibility
AVAILABLE_MODELS = list(AVAILABLE_VOICES.keys())

# Validate environment variables
if not RUNPOD_API_KEY:
    logger.warning("RUNPOD_API_KEY not found in Django settings")
if not JWT_SECRET:
    logger.warning("JWT_SECRET not found in Django settings")

def generate_tts(text, model="chatterbox", force_gtts=False, force_runpod=False):
    """
    Generate TTS audio using RunPod API with gTTS fallback
    Models available: chatterbox
    """
    
    # Clean and validate text
    if not text or not text.strip():
        logger.error("Empty text provided for TTS")
        return None
    
    clean_text = text.strip()
    if len(clean_text) > 5000:
        clean_text = clean_text[:5000]
        logger.warning("Text truncated to 5000 characters for TTS")
    
    # Use gTTS fallback if requested
    if force_gtts:
        logger.info("Using gTTS fallback as requested")
        return generate_gtts_fallback(clean_text)
    
    # Check if we have RunPod credentials
    if not RUNPOD_API_KEY or not JWT_SECRET:
        logger.warning("RunPod credentials missing, using gTTS fallback")
        if not force_runpod:
            return generate_gtts_fallback(clean_text)
        else:
            logger.error("RunPod credentials missing and force_runpod=True")
            return None
    
    # Try RunPod API first
    logger.info(f"🚀 Attempting RunPod TTS with model: {model}")
    logger.info(f"🔑 API Key present: {bool(RUNPOD_API_KEY)}")
    logger.info(f"🔐 JWT Secret present: {bool(JWT_SECRET)}")
    
    runpod_result = generate_runpod_tts(clean_text, model)
    
    if runpod_result:
        logger.info(f"✅ RunPod TTS successful: {runpod_result}")
        return runpod_result
    
    # If force_runpod is True, don't fallback to gTTS
    if force_runpod:
        logger.error("❌ RunPod TTS failed and force_runpod=True, returning None")
        return None
    
    # Fallback to gTTS if RunPod fails
    logger.warning("⚠️  RunPod TTS failed, falling back to gTTS")
    return generate_gtts_fallback(clean_text)

def generate_runpod_tts(text, model="chatterbox"):
    """
    Generate TTS using RunPod API with chatterbox model and female_default voice
    Available models: chatterbox
    """
    try:
        # Validate voice model
        if model not in AVAILABLE_VOICES:
            logger.warning(f"Invalid voice '{model}', using 'chatterbox'")
            model = "chatterbox"
        
        voice_config = AVAILABLE_VOICES[model]
        voice_id = voice_config["voice_id"]
        
        logger.info(f"RunPod TTS generation with model '{model}' for: '{text[:50]}...'")
        
        # Create filename for caching (use .mp3 since RunPod returns MP3)
        text_hash = hashlib.md5(f"{text}_chatterbox_female_default".encode()).hexdigest()[:8]
        filename = f"runpod_chatterbox_female_default_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check if file already exists (caching)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            media_url = f"/media/tts/{filename}"
            logger.info(f"Using cached RunPod TTS: {media_url}")
            return media_url
        
        # Prepare RunPod API request
        headers = {
            "Authorization": f"Bearer {RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Updated payload format for chatterbox model with female_default voice
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
        
        # Make API request
        logger.info(f"Sending request to RunPod API: {RUNPOD_ENDPOINT}")
        logger.info(f"Request headers: {headers}")
        logger.info(f"Request payload: {payload}")
        
        response = requests.post(
            RUNPOD_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        logger.info(f"RunPod API response status: {response.status_code}")
        logger.info(f"RunPod API response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"RunPod API response: {result}")
            
            # Check if the response contains audio data
            if "output" in result and result["output"]:
                output = result["output"]
                
                # Handle nested RunPod response structure
                audio_base64 = None
                
                # Try to find audio_base64 in nested structure
                if isinstance(output, dict):
                    # Check direct audio fields
                    if "audio_base64" in output:
                        audio_base64 = output["audio_base64"]
                    elif "audio_data" in output:
                        audio_base64 = output["audio_data"]
                    # Check nested result structure
                    elif "result" in output and isinstance(output["result"], dict):
                        nested_result = output["result"]
                        if "output" in nested_result and isinstance(nested_result["output"], dict):
                            nested_output = nested_result["output"]
                            if "output" in nested_output and isinstance(nested_output["output"], dict):
                                final_output = nested_output["output"]
                                if "audio_base64" in final_output:
                                    audio_base64 = final_output["audio_base64"]
                
                # Convert base64 to audio file
                if audio_base64:
                    try:
                        import base64
                        audio_data = base64.b64decode(audio_base64)
                        with open(filepath, 'wb') as f:
                            f.write(audio_data)
                        logger.info(f"Successfully decoded base64 audio data")
                    except Exception as e:
                        logger.error(f"Failed to decode base64 audio: {e}")
                        return None
                else:
                    logger.error(f"No audio_base64 found in response: {output}")
                    return None

                
                # Verify file was created and has content
                if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                    media_url = f"/media/tts/{filename}"
                    logger.info(f"RunPod TTS complete: {media_url} ({os.path.getsize(filepath)} bytes)")
                    return media_url
                else:
                    logger.error("RunPod TTS file creation failed or file too small")
                    if os.path.exists(filepath):
                        os.remove(filepath)
            else:
                logger.error(f"No output in RunPod response: {result}")
        else:
            logger.error(f"RunPod API error: {response.status_code}")
            logger.error(f"Response text: {response.text}")
            logger.error(f"Response headers: {dict(response.headers)}")
            
            # Try to parse error response
            try:
                error_data = response.json()
                logger.error(f"Error JSON: {error_data}")
            except:
                logger.error("Could not parse error response as JSON")
            
    except requests.exceptions.Timeout:
        logger.error("RunPod API request timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"RunPod API request failed: {e}")
    except Exception as e:
        logger.error(f"RunPod TTS generation failed: {type(e).__name__}: {e}")
    
    return None

def generate_gtts_fallback(text, max_retries=1):
    """
    Generate TTS using gTTS - optimized for speed and reliability
    """
    try:
        logger.info(f"Fast gTTS generation for: '{text[:50]}...'")
        
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
                logger.info(f"Fast gTTS complete: {media_url} ({file_size} bytes)")
                return media_url
            else:
                logger.warning(f"gTTS file too small: {file_size} bytes")
                if os.path.exists(filepath):
                    os.remove(filepath)
        
    except Exception as e:
        logger.error(f"Fast gTTS failed: {type(e).__name__}: {e}")
    
    return None

def test_tts_generation(test_text=None):
    """
    Test function to debug TTS generation with comprehensive testing
    """
    if test_text is None:
        test_text = "Hello, this is a test of the text to speech system. Can you hear me clearly?"
    
    logger.info(f"Testing TTS with text: '{test_text}'")
    
    # Test primary TTS
    logger.info("Testing primary TTS API...")
    result = generate_tts(test_text)
    
    if result:
        logger.info(f"TTS test successful: {result}")
        
        # Verify file exists
        full_path = os.path.join(settings.BASE_DIR, result.lstrip('/'))
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            logger.info(f"File verified at: {full_path} ({file_size} bytes)")
            
            # Additional file validation
            if result.endswith('.wav'):
                # Basic WAV file validation
                with open(full_path, 'rb') as f:
                    header = f.read(12)
                    if header[:4] == b'RIFF' and header[8:12] == b'WAVE':
                        logger.info("Valid WAV file structure")
                    else:
                        logger.warning("Invalid WAV file structure")
            elif result.endswith('.mp3'):
                # Basic MP3 file validation
                with open(full_path, 'rb') as f:
                    header = f.read(3)
                    if header == b'ID3' or header[:2] == b'\xff\xfb':
                        logger.info("Valid MP3 file structure")
                    else:
                        logger.warning("Invalid MP3 file structure")
        else:
            logger.error(f"File not found at: {full_path}")
            return None
    else:
        logger.error("TTS test failed")
        
        # Test gTTS directly
        logger.info("Testing gTTS fallback directly...")
        gtts_result = generate_gtts_fallback(test_text)
        if gtts_result:
            logger.info(f"gTTS direct test successful: {gtts_result}")
            result = gtts_result
        else:
            logger.error("gTTS direct test also failed")
    
    return result

def cleanup_old_tts_files(days_old=1):
    """
    Clean up TTS files older than specified days
    """
    try:
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        if not os.path.exists(tts_dir):
            logger.info("TTS directory doesn't exist, nothing to clean")
            return
            
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        cleaned_count = 0
        total_size = 0
        
        for filename in os.listdir(tts_dir):
            filepath = os.path.join(tts_dir, filename)
            if os.path.isfile(filepath):
                file_modified = os.path.getmtime(filepath)
                if file_modified < cutoff_time:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    cleaned_count += 1
                    total_size += file_size
                    
        logger.info(f"Cleaned up {cleaned_count} old TTS files ({total_size} bytes)")
        
    except Exception as e:
        logger.error(f"TTS cleanup failed: {e}")

# Alias for backwards compatibility
generate_tts_audio = generate_tts

# Export sync helper functions
__all__ = [
    'generate_tts',
    'generate_runpod_tts', 
    'generate_gtts_fallback',
    'test_tts_generation',
    'check_tts_system',
    'estimate_audio_duration',
    'get_audio_duration',
    'create_typewriter_sync_data',
    'ensure_audio_sync_data',
    'test_typewriter_sync_system'
]

# Helper function to switch models easily
def generate_tts_chatterbox(text):
    """Generate TTS using chatterbox model with female_default voice"""
    return generate_tts(text, model="chatterbox")

def generate_tts_female_default(text):
    """Generate TTS using female_default voice in chatterbox model"""
    return generate_tts(text, model="chatterbox")

def test_chatterbox_voice(text="Hello! I'm your AI interviewer using the female default voice. Let's begin the interview."):
    """Test specifically the chatterbox model with female_default voice"""
    logger.info("Testing chatterbox model with female_default voice specifically...")
    
    # Force RunPod API (no fallback to gTTS)
    try:
        result = generate_runpod_tts(text, "chatterbox")
        if result:
            logger.info(f"✅ Chatterbox female_default voice test successful: {result}")
            return result
        else:
            logger.error("❌ Chatterbox female_default voice test failed - no audio generated")
            return None
    except Exception as e:
        logger.error(f"❌ Chatterbox female_default voice test error: {e}")
        return None

def check_tts_system():
    """
    Comprehensive TTS system health check
    """
    logger.info("Starting TTS system health check...")
    
    health_info = {
        'media_root': settings.MEDIA_ROOT,
        'media_url': settings.MEDIA_URL,
        'tts_dir_exists': os.path.exists(os.path.join(settings.MEDIA_ROOT, 'tts')),
        'runpod_endpoint': RUNPOD_ENDPOINT,
        'available_voices': AVAILABLE_VOICES,
        'available_models': list(AVAILABLE_VOICES.keys()),
    }
    
    # Check if we can create TTS directory
    try:
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        health_info['can_create_tts_dir'] = True
        
        # Test write permissions
        test_file = os.path.join(tts_dir, 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        health_info['write_permission'] = True
        
    except Exception as e:
        health_info['can_create_tts_dir'] = False
        health_info['write_permission'] = False
        health_info['tts_dir_error'] = str(e)
    
    # Test gTTS availability
    try:
        from gtts import gTTS
        health_info['gtts_available'] = True
        
        # Test gTTS functionality
        test_tts = gTTS(text="test", lang='en')
        health_info['gtts_functional'] = True
        
    except ImportError as e:
        health_info['gtts_available'] = False
        health_info['gtts_error'] = str(e)
    except Exception as e:
        health_info['gtts_available'] = True
        health_info['gtts_functional'] = False
        health_info['gtts_error'] = str(e)
    
    # Test RunPod API connectivity
    try:
        headers = {
            "Authorization": f"Bearer {RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        }
        
        test_payload = {
            "input": {
                "text": "test",
                "model": "chatterbox",
                "voice_id": "female_default",
                "jwt_token": JWT_SECRET
            }
        }
        
        response = requests.post(
            RUNPOD_ENDPOINT,
            headers=headers,
            json=test_payload,
            timeout=10
        )
        
        health_info['runpod_api_reachable'] = True
        health_info['runpod_api_status'] = response.status_code
        health_info['runpod_api_response_time'] = response.elapsed.total_seconds()
        
        if response.status_code == 200:
            health_info['runpod_api_functional'] = True
        else:
            health_info['runpod_api_functional'] = False
            health_info['runpod_api_error'] = response.text
            
    except Exception as e:
        health_info['runpod_api_reachable'] = False
        health_info['runpod_api_error'] = str(e)
    
    # Test actual TTS generation
    try:
        test_result = generate_tts("Hello world", force_gtts=True)  # Force gTTS for reliable test
        health_info['test_generation'] = bool(test_result)
        if test_result:
            full_path = os.path.join(settings.BASE_DIR, test_result.lstrip('/'))
            health_info['test_file_exists'] = os.path.exists(full_path)
            if os.path.exists(full_path):
                health_info['test_file_size'] = os.path.getsize(full_path)
    except Exception as e:
        health_info['test_generation'] = False
        health_info['test_error'] = str(e)
    
    logger.info("TTS System Health Check Results:")
    for key, value in health_info.items():
        logger.info(f"   {key}: {value}")
    
    return health_info

def get_tts_with_fallback_chain(text):
    """
    Try multiple TTS methods in order with comprehensive fallback
    """
    methods = [
        ('RunPod chatterbox female_default', lambda: generate_tts(text, model="chatterbox")),
        ('gTTS Fallback', lambda: generate_gtts_fallback(text)),
        ('Emergency Text', lambda: create_emergency_response())
    ]
    
    for method_name, method_func in methods:
        try:
            logger.info(f"Trying {method_name}...")
            result = method_func()
            if result:
                logger.info(f"{method_name} succeeded: {result}")
                return result
            else:
                logger.warning(f"{method_name} returned None")
        except Exception as e:
            logger.error(f"{method_name} failed: {e}")
    
    logger.error("All TTS methods failed")
    return None

def estimate_audio_duration(text, words_per_minute=140):
    """
    Estimate audio duration based on text length and speaking rate
    Default speaking rate: 140 words per minute (slightly slower for better sync)
    """
    if not text or not text.strip():
        return 2.0
    
    # Count words
    word_count = len(text.split())
    
    # Calculate duration in seconds
    duration_seconds = (word_count / words_per_minute) * 60
    
    # Add padding for natural pauses and punctuation (15% extra)
    duration_seconds *= 1.15
    
    # Minimum duration of 2 seconds, maximum of 30 seconds
    duration_seconds = max(2.0, min(duration_seconds, 30.0))
    
    return duration_seconds

def get_audio_duration(audio_path):
    """
    Get actual audio duration from file (requires mutagen library)
    Falls back to estimation if mutagen is not available
    """
    try:
        # Try to get actual duration using mutagen
        try:
            from mutagen import File
            audio_file = File(audio_path)
            if audio_file and audio_file.info:
                return audio_file.info.length
        except ImportError:
            logger.warning("Mutagen not available, using estimation")
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
        
        # Fallback: estimate based on file size (rough approximation)
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            # Rough estimate: 1KB per second for compressed audio
            estimated_duration = file_size / 1024
            return max(2.0, min(estimated_duration, 30.0))  # Cap between 2-30 seconds
        
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
    
    return None

def create_emergency_response():
    """
    Create a simple text response when all audio generation fails
    """
    return "TEXT_ONLY_RESPONSE"

def get_audio_duration_with_fallback(audio_path, text):
    """
    Get audio duration with multiple fallback methods
    """
    # Try to get actual duration first
    actual_duration = get_audio_duration(audio_path)
    if actual_duration and actual_duration > 0:
        logger.info(f"Using actual audio duration: {actual_duration} seconds")
        return actual_duration
    
    # Fallback to estimation
    estimated_duration = estimate_audio_duration(text)
    logger.info(f"Using estimated audio duration: {estimated_duration} seconds")
    return estimated_duration

def ensure_audio_sync_data(audio_url, text):
    """
    Ensure we have proper duration data for audio synchronization
    """
    if not audio_url or not text:
        return None
    
    try:
        # Get full path
        full_path = os.path.join(settings.BASE_DIR, audio_url.lstrip('/'))
        
        # Get duration with fallback
        duration = get_audio_duration_with_fallback(full_path, text)
        
        return {
            'audio_url': audio_url,
            'duration': duration,
            'text_length': len(text),
            'word_count': len(text.split()),
            'estimated_chars_per_second': len(text) / duration if duration > 0 else 20
        }
        
    except Exception as e:
        logger.error(f"Error ensuring audio sync data: {e}")
        return {
            'audio_url': audio_url,
            'duration': estimate_audio_duration(text),
            'text_length': len(text),
            'word_count': len(text.split()),
            'estimated_chars_per_second': 20
        }

def create_typewriter_sync_data(text, audio_url=None, audio_duration=None):
    """
    Create synchronization data for typewriter effects
    """
    sync_data = {
        'text': text,
        'text_length': len(text),
        'word_count': len(text.split()),
        'has_audio': bool(audio_url and audio_url.strip() and audio_url != 'None'),
        'audio_url': audio_url if audio_url and audio_url != 'None' else None,
    }
    
    if sync_data['has_audio']:
        # Use provided duration or estimate
        if audio_duration and audio_duration > 0:
            sync_data['duration'] = audio_duration
        else:
            sync_data['duration'] = estimate_audio_duration(text)
        
        # Calculate typing speeds
        sync_data['chars_per_second'] = sync_data['text_length'] / sync_data['duration']
        sync_data['ms_per_char'] = (sync_data['duration'] * 1000) / sync_data['text_length']
    else:
        # Natural typing without audio
        sync_data['duration'] = estimate_audio_duration(text)
        sync_data['chars_per_second'] = 20  # Natural typing speed
        sync_data['ms_per_char'] = 50  # 50ms per character
    
    return sync_data

def test_runpod_integration(test_text="Hello, this is a test of the RunPod TTS system with chatterbox model and female_default voice."):
    """
    Test function specifically for RunPod TTS integration with chatterbox model
    """
    logger.info("=== RunPod TTS Integration Test (Chatterbox Model) ===")
    logger.info(f"Testing with text: '{test_text}'")
    
    results = {}
    
    # Test chatterbox model with female_default voice
    for model in AVAILABLE_VOICES.keys():
        logger.info(f"\nTesting model: {model} with female_default voice")
        try:
            result = generate_runpod_tts(test_text, model)
            if result:
                results[model] = {
                    'status': 'success',
                    'url': result,
                    'file_path': os.path.join(settings.BASE_DIR, result.lstrip('/'))
                }
                
                # Check if file exists
                full_path = os.path.join(settings.BASE_DIR, result.lstrip('/'))
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    results[model]['file_size'] = file_size
                    logger.info(f"✓ {model} model with female_default voice successful: {result} ({file_size} bytes)")
                else:
                    results[model]['status'] = 'file_not_found'
                    logger.error(f"✗ {model} model: File not found at {full_path}")
            else:
                results[model] = {'status': 'failed', 'error': 'No result returned'}
                logger.error(f"✗ {model} model failed")
        except Exception as e:
            results[model] = {'status': 'error', 'error': str(e)}
            logger.error(f"✗ {model} model error: {e}")
    
    # Test fallback chain
    logger.info("\nTesting complete fallback chain...")
    try:
        fallback_result = get_tts_with_fallback_chain(test_text)
        if fallback_result:
            results['fallback_chain'] = {'status': 'success', 'result': fallback_result}
            logger.info(f"✓ Fallback chain successful: {fallback_result}")
        else:
            results['fallback_chain'] = {'status': 'failed'}
            logger.error("✗ Fallback chain failed")
    except Exception as e:
        results['fallback_chain'] = {'status': 'error', 'error': str(e)}
        logger.error(f"✗ Fallback chain error: {e}")
    
    logger.info("\n=== Test Results Summary ===")
    for key, value in results.items():
        logger.info(f"{key}: {value}")
    
    return results

def test_typewriter_sync_system(test_text="Hello! Welcome to your AI interview. I'm excited to learn more about you and understand what makes you a great candidate for this position."):
    """
    Test the typewriter synchronization system
    """
    logger.info("=== Typewriter Sync System Test ===")
    
    # Generate audio for testing
    audio_url = generate_tts(test_text)
    
    if audio_url:
        # Create sync data
        sync_data = create_typewriter_sync_data(test_text, audio_url)
        logger.info(f"Sync data created: {sync_data}")
        
        # Test duration estimation
        estimated = estimate_audio_duration(test_text)
        logger.info(f"Estimated duration: {estimated} seconds")
        
        # Test actual duration if possible
        full_path = os.path.join(settings.BASE_DIR, audio_url.lstrip('/'))
        actual = get_audio_duration(full_path)
        if actual:
            logger.info(f"Actual duration: {actual} seconds")
        
        return {
            'success': True,
            'audio_url': audio_url,
            'sync_data': sync_data,
            'estimated_duration': estimated,
            'actual_duration': actual
        }
    else:
        logger.error("Could not generate audio for typewriter sync test")
        return {
            'success': False,
            'error': 'Audio generation failed'
        }