import requests
import os
from gtts import gTTS
from django.conf import settings
import uuid
import tempfile
import time
import logging

# Set up logging
logger = logging.getLogger(__name__)

def generate_tts(text, voice_id="female_default", force_gtts=False):
    """
    Generate TTS audio with primary API and gTTS fallback
    Enhanced with better error handling and connection testing
    """
    
    # Clean and validate text
    if not text or not text.strip():
        logger.error("Empty text provided for TTS")
        return None
    
    clean_text = text.strip()
    if len(clean_text) > 5000:
        clean_text = clean_text[:5000]
        logger.warning("Text truncated to 5000 characters for TTS")
    
    # Skip primary API if force_gtts is True
    if force_gtts:
        logger.info("Forcing gTTS fallback")
        return generate_gtts_fallback(clean_text)
    
    # FIXED: Correct API base URL (remove /docs/)
    TTS_BASE_URL = "https://mjgqbrf2sl7dqj-8000.proxy.runpod.net"
    
    try:
        logger.info(f"Starting TTS generation for: '{clean_text[:50]}...'")
        logger.info(f"Using API URL: {TTS_BASE_URL}")
        
        # Test API connectivity first
        try:
            connectivity_response = requests.get(f"{TTS_BASE_URL}/health", timeout=5)
            logger.info(f"API health check: {connectivity_response.status_code}")
        except:
            logger.warning("API health check failed, proceeding anyway")
        
        payload = {
            'text': clean_text,
            'voice_id': voice_id,
            'exaggeration': 0.5,
            'temperature': 0.3,
            'cfg_weight': 0.5,
            'seed': 0
        }
        
        logger.info(f"Request payload: {payload}")
        
        # Step 1: Synthesize speech with shorter timeout
        synthesize_url = f"{TTS_BASE_URL}/synthesize"
        logger.info(f"Sending POST request to: {synthesize_url}")
        
        response = requests.post(
            synthesize_url,
            json=payload,
            timeout=8,  # Further reduced timeout for speed
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                logger.info(f"API Response: {result}")
                
                if result.get('success') and result.get('audio_id'):
                    audio_id = result['audio_id']
                    logger.info(f"Audio ID received: {audio_id}")
                    
                    # Step 2: Download audio with retry logic
                    audio_url = f"{TTS_BASE_URL}/audio/{audio_id}"
                    logger.info(f"Downloading audio from: {audio_url}")
                    
                    # Retry logic for audio download
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            audio_response = requests.get(audio_url, timeout=15)
                            logger.info(f"Audio download attempt {attempt + 1}: {audio_response.status_code}")
                            
                            if audio_response.status_code == 200:
                                content_length = len(audio_response.content)
                                logger.info(f"Audio content length: {content_length} bytes")
                                
                                if content_length > 100:  # Minimum valid audio file size
                                    # Save audio file
                                    filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
                                    tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
                                    os.makedirs(tts_dir, exist_ok=True)
                                    filepath = os.path.join(tts_dir, filename)
                                    
                                    logger.info(f"Saving audio to: {filepath}")
                                    
                                    with open(filepath, 'wb') as f:
                                        f.write(audio_response.content)
                                    
                                    # Verify file was created and has content
                                    if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                                        file_size = os.path.getsize(filepath)
                                        logger.info(f"Audio file saved successfully: {filepath} ({file_size} bytes)")
                                        
                                        media_url = f"/media/tts/{filename}"
                                        logger.info(f"Media URL: {media_url}")
                                        return media_url
                                    else:
                                        logger.error("Saved file is empty or too small")
                                        if os.path.exists(filepath):
                                            os.remove(filepath)
                                        continue
                                else:
                                    logger.warning("Audio content too small, retrying...")
                                    time.sleep(1)  # Wait before retry
                                    continue
                            else:
                                logger.warning(f"Audio download failed with status {audio_response.status_code}")
                                if attempt < max_retries - 1:
                                    time.sleep(1)
                                    continue
                                
                        except requests.exceptions.Timeout:
                            logger.warning(f"Audio download timeout on attempt {attempt + 1}")
                            if attempt < max_retries - 1:
                                time.sleep(1)
                                continue
                        except Exception as e:
                            logger.warning(f"Audio download error on attempt {attempt + 1}: {e}")
                            if attempt < max_retries - 1:
                                time.sleep(1)
                                continue
                    
                    # If all retries failed
                    raise Exception("Audio download failed after all retries")
                        
                else:
                    logger.error(f"Invalid API response structure: {result}")
                    if 'error' in result:
                        logger.error(f"API Error: {result['error']}")
                    raise Exception("API returned invalid response structure")
                    
            except ValueError as json_error:
                logger.error(f"JSON decode error: {json_error}")
                logger.error(f"Raw response content: {response.text[:200]}...")
                raise Exception(f"Invalid JSON response: {json_error}")
                
        else:
            logger.error(f"API request failed with status: {response.status_code}")
            logger.error(f"Response content: {response.text[:200]}...")
            
            # Try to parse error message
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    logger.error(f"API Error detail: {error_data['detail']}")
            except:
                pass
                
            raise Exception(f"API request failed with status {response.status_code}")
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout after 15 seconds")
        logger.info("Falling back to gTTS...")
        return generate_gtts_fallback(clean_text)
        
    except requests.exceptions.ConnectionError as conn_error:
        logger.error(f"Connection error: {conn_error}")
        logger.info("Falling back to gTTS...")
        return generate_gtts_fallback(clean_text)
        
    except Exception as e:
        logger.error(f"Primary TTS failed: {type(e).__name__}: {e}")
        logger.info("Falling back to gTTS...")
        return generate_gtts_fallback(clean_text)

def generate_gtts_fallback(text, max_retries=2):  # Reduced retries
    """
    Generate TTS using gTTS as fallback with enhanced error handling and retry logic
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Starting gTTS fallback attempt {attempt + 1} for: '{text[:50]}...'")
            
            # Clean text for gTTS
            clean_text = text.strip()
            if not clean_text:
                logger.error("Empty text provided to gTTS")
                return None
                
            if len(clean_text) > 5000:  # gTTS has character limits
                clean_text = clean_text[:5000]
                logger.warning("Text truncated to 5000 characters for gTTS")
            
            filename = f"gtts_{uuid.uuid4().hex[:8]}.mp3"
            tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
            os.makedirs(tts_dir, exist_ok=True)
            filepath = os.path.join(tts_dir, filename)
            
            logger.info("Generating gTTS audio...")
            
            # Generate gTTS with error handling
            tts = gTTS(text=clean_text, lang='en', slow=False)
            tts.save(filepath)
            
            # Wait a moment for file to be written
            time.sleep(0.5)
            
            # Verify file was created and has content
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"gTTS file created: {filepath} ({file_size} bytes)")
                
                if file_size > 500:  # Reduced minimum size for speed
                    media_url = f"/media/tts/{filename}"
                    logger.info(f"gTTS Media URL: {media_url}")
                    return media_url
                else:
                    logger.warning(f"gTTS file too small: {file_size} bytes")
                    os.remove(filepath)  # Clean up small file
                    if attempt < max_retries - 1:
                        time.sleep(0.5)  # Reduced wait time
                        continue
            else:
                logger.warning("gTTS file was not created")
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Reduced wait time
                    continue
                    
        except Exception as e:
            logger.error(f"gTTS attempt {attempt + 1} failed: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Reduced wait time between retries
                continue
            else:
                logger.error("All gTTS attempts failed")
    
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

def check_tts_system():
    """
    Comprehensive TTS system health check
    """
    logger.info("Starting TTS system health check...")
    
    health_info = {
        'media_root': settings.MEDIA_ROOT,
        'media_url': settings.MEDIA_URL,
        'tts_dir_exists': os.path.exists(os.path.join(settings.MEDIA_ROOT, 'tts')),
        'tts_api_url': "https://mjgqbrf2sl7dqj-8000.proxy.runpod.net",
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
    
    # Check network connectivity to TTS API with detailed testing
    try:
        response = requests.get("https://mjgqbrf2sl7dqj-8000.proxy.runpod.net", timeout=10)
        health_info['api_reachable'] = True
        health_info['api_status'] = response.status_code
        health_info['api_response_time'] = response.elapsed.total_seconds()
        
        # Test the synthesize endpoint
        try:
            test_payload = {'text': 'test', 'voice_id': 'female_default'}
            synth_response = requests.post(
                "https://mjgqbrf2sl7dqj-8000.proxy.runpod.net/synthesize",
                json=test_payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            health_info['synthesize_endpoint'] = synth_response.status_code
        except Exception as e:
            health_info['synthesize_endpoint'] = f"Error: {e}"
            
    except Exception as e:
        health_info['api_reachable'] = False
        health_info['api_error'] = str(e)
    
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
        ('Primary API', lambda: generate_tts(text, force_gtts=False)),
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

def create_emergency_response():
    """
    Create a simple text response when all audio generation fails
    """
    return "TEXT_ONLY_RESPONSE"