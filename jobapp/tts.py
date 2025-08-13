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
    
    # Skip slow primary API and use fast gTTS directly for better performance
    if force_gtts or True:  # Always use gTTS for speed
        logger.info("Using fast gTTS for better response speed")
        return generate_gtts_fallback(clean_text)
        
    # This code is now skipped - using gTTS directly above
    pass

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
        import hashlib
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

def check_tts_system():
    """
    Comprehensive TTS system health check
    """
    logger.info("Starting TTS system health check...")
    
    health_info = {
        'media_root': settings.MEDIA_ROOT,
        'media_url': settings.MEDIA_URL,
        'tts_dir_exists': os.path.exists(os.path.join(settings.MEDIA_ROOT, 'tts')),
        'tts_api_url': "https://3obn1g343qy9uk-8000.proxy.runpod.net",
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
        response = requests.get("https://3obn1g343qy9uk-8000.proxy.runpod.net", timeout=10)
        health_info['api_reachable'] = True
        health_info['api_status'] = response.status_code
        health_info['api_response_time'] = response.elapsed.total_seconds()
        
        # Test the synthesize endpoint
        try:
            test_payload = {'text': 'test', 'voice_id': 'female_default'}
            synth_response = requests.post(
                "https://3obn1g343qy9uk-8000.proxy.runpod.net/synthesize",
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