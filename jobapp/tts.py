"""
TTS.PY - Configured for Daisy Studious voice using new TTS API
"""
import requests
import os
from gtts import gTTS
from django.conf import settings
import hashlib
import logging
from django.utils import timezone

# Set up logging
logger = logging.getLogger(__name__)

# New TTS API Configuration
NEW_TTS_API_KEY = getattr(settings, 'NEW_TTS_API_KEY', '') or os.environ.get('NEW_TTS_API_KEY', '')
NEW_TTS_API_URL = "http://54.89.117.239"
NEW_TTS_VOICE_ID = "Daisy Studious"
NEW_TTS_MODEL_ID = "coqui"

if NEW_TTS_API_KEY:
    NEW_TTS_API_KEY = NEW_TTS_API_KEY.strip()

# YOUR SPECIFIC VOICE CONFIGURATION - Daisy Studious Only
DAISY_VOICE_ID = NEW_TTS_VOICE_ID or "Daisy Studious"
DAISY_VOICE_NAME = "Daisy Studious - Natural Conversations"

# All voice requests will use Daisy Studious
VOICE_OPTIONS = {
    "female_interview": {
        "voice_id": DAISY_VOICE_ID,
        "name": DAISY_VOICE_NAME,
        "model": NEW_TTS_MODEL_ID or "coqui"
    },
    "female_natural": {
        "voice_id": DAISY_VOICE_ID,
        "name": DAISY_VOICE_NAME,
        "model": NEW_TTS_MODEL_ID or "coqui"
    },
    "female_professional": {
        "voice_id": DAISY_VOICE_ID,
        "name": DAISY_VOICE_NAME,
        "model": NEW_TTS_MODEL_ID or "coqui"
    },
    "default": {
        "voice_id": DAISY_VOICE_ID,
        "name": DAISY_VOICE_NAME,
        "model": NEW_TTS_MODEL_ID or "coqui"
    }
}

def check_elevenlabs_status():
    """Check if new TTS API is working with Daisy voice access"""
    if not NEW_TTS_API_KEY:
        return False, "New TTS API key not configured"
    
    if len(NEW_TTS_API_KEY) < 20:
        return False, "New TTS API key appears invalid (too short)"
    
    if not NEW_TTS_API_URL:
        return False, "New TTS API URL not configured"
    
    try:
        headers = {
            'Authorization': f'Bearer {NEW_TTS_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        logger.info("Testing new TTS API connection...")
        
        # Test API endpoint
        test_url = f"{NEW_TTS_API_URL.rstrip('/')}/health"
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            logger.info(f"New TTS API health check response: {response.status_code}")
        except:
            # If health endpoint doesn't exist, that's okay
            logger.info("Health endpoint not available, proceeding with main API test")
        
        # Test with a simple TTS request
        test_payload = {
            "text": "Hello, this is a test.",
            "voice_id": DAISY_VOICE_ID,
            "model_id": NEW_TTS_MODEL_ID or "coqui"
        }
        
        tts_url = f"{NEW_TTS_API_URL.rstrip('/')}/v1/text-to-speech"
        response = requests.post(tts_url, json=test_payload, headers=headers, timeout=15)
        
        logger.info(f"New TTS API test response: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"Daisy voice accessible via new TTS API")
            return True, f"API working - Daisy voice accessible"
        elif response.status_code == 401:
            return False, "Authentication failed - check API key"
        elif response.status_code == 404:
            return False, f"Daisy voice (ID: {DAISY_VOICE_ID}) not found"
        else:
            logger.warning(f"API test failed: {response.status_code}")
            return False, f"API error: HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        logger.error("New TTS API timeout")
        return False, "API request timed out"
    except requests.exceptions.ConnectionError:
        logger.error("New TTS API connection error") 
        return False, "Cannot connect to TTS API servers"
    except Exception as e:
        logger.error(f"New TTS API status check failed: {e}")
        return False, f"Connection error: {str(e)[:100]}"

def generate_elevenlabs_tts(text, voice="female_interview"):
    """Generate TTS using new API with Daisy Studious voice only"""
    try:
        if not NEW_TTS_API_KEY or not NEW_TTS_API_URL:
            logger.warning("New TTS API not configured, falling back to Google TTS")
            return generate_google_tts(text)
        
        # Always use Daisy voice regardless of voice parameter
        voice_config = VOICE_OPTIONS.get(voice, VOICE_OPTIONS["default"])
        voice_id = DAISY_VOICE_ID  # Force Daisy voice
        model_id = voice_config["model"]
        
        logger.info(f"Generating TTS with Daisy Studious voice (ID: {voice_id})")
        logger.info(f"Text length: {len(text)} characters")
        
        # Clean and validate text
        clean_text = text.strip()
        if len(clean_text) > 2000:  # Reasonable character limit
            clean_text = clean_text[:1997] + "..."
            logger.info(f"Text truncated to {len(clean_text)} characters")
        
        # Create filename for caching
        text_hash = hashlib.md5(f"{clean_text}_daisy_studious".encode()).hexdigest()[:10]
        filename = f"daisy_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check cache first
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            media_url = f"/media/tts/{filename}"
            logger.info(f"Using cached Daisy voice TTS: {media_url}")
            return media_url
        
        # Prepare API request
        url = f"{NEW_TTS_API_URL.rstrip('/')}/v1/text-to-speech"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {NEW_TTS_API_KEY}"
        }
        
        # Payload for new TTS API
        payload = {
            "text": clean_text,
            "voice_id": voice_id,
            "model_id": model_id,
            "settings": {
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            }
        }
        
        logger.info(f"Making request to new TTS API: {url}")
        logger.info(f"Using model: {model_id} for Daisy voice")
        
        # Make the API request with retry
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=25)
                
                logger.info(f"New TTS API response: {response.status_code} (attempt {attempt + 1})")
                
                if response.status_code == 200:
                    # Save the audio file
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    # Verify file was created successfully
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                        media_url = f"/media/tts/{filename}"
                        file_size = os.path.getsize(filepath)
                        logger.info(f"Daisy TTS generated successfully: {media_url} ({file_size} bytes)")
                        return media_url
                    else:
                        logger.error("Generated audio file is too small or empty")
                        if os.path.exists(filepath):
                            os.remove(filepath)
                        
                elif response.status_code == 401:
                    logger.error("Authentication failed - check API key")
                    break
                elif response.status_code == 429:
                    logger.warning(f"Rate limit hit, retrying in {2 ** attempt} seconds...")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)
                        continue
                else:
                    logger.error(f"API error {response.status_code}: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    continue
        
        # If all attempts failed, fall back to Google TTS
        logger.warning("New TTS API failed, falling back to Google TTS")
        return generate_google_tts(text)
        
    except Exception as e:
        logger.error(f"Unexpected error in Daisy TTS generation: {e}")
        return generate_google_tts(text)

def generate_google_tts(text, voice="female_interview"):
    """Fallback Google TTS generation"""
    try:
        logger.info("Using Google TTS as fallback")
        
        # Clean text
        clean_text = text.strip()
        if len(clean_text) > 1000:
            clean_text = clean_text[:997] + "..."
        
        # Create filename
        text_hash = hashlib.md5(f"{clean_text}_google".encode()).hexdigest()[:10]
        filename = f"gtts_{text_hash}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Check cache
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            media_url = f"/media/tts/{filename}"
            logger.info(f"Using cached Google TTS: {media_url}")
            return media_url
        
        # Generate with Google TTS
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(filepath)
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            media_url = f"/media/tts/{filename}"
            logger.info(f"Google TTS generated: {media_url}")
            return media_url
        else:
            logger.error("Google TTS generation failed")
            return None
            
    except Exception as e:
        logger.error(f"Google TTS fallback failed: {e}")
        return None

# Alias for backward compatibility
def generate_tts(text, voice="female_interview"):
    """Main TTS generation function - uses Daisy voice via new API"""
    return generate_elevenlabs_tts(text, voice)

def estimate_audio_duration(text):
    """Estimate audio duration based on text length"""
    # Average speaking rate is about 150-160 words per minute
    # Average word length is about 5 characters
    # So roughly 750-800 characters per minute
    words = len(text.split())
    # Assume 150 words per minute speaking rate
    duration_minutes = words / 150
    duration_seconds = duration_minutes * 60
    # Add some padding for natural pauses
    duration_seconds = max(3.0, duration_seconds + 1.0)
    return duration_seconds

def get_audio_duration(file_path):
    """Get actual audio duration from file (fallback to estimation)"""
    try:
        import os
        if not os.path.exists(file_path):
            return None
        
        # For now, return None to fall back to estimation
        # In the future, you could add audio file analysis here
        return None
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return None

# Test functions for the new API
def test_daisy_voice_only():
    """Test Daisy voice generation"""
    test_text = "Hello! I'm Daisy Studious, your AI interviewer. Let's begin our conversation."
    logger.info("Testing Daisy voice generation...")
    
    result = generate_elevenlabs_tts(test_text, "female_interview")
    
    if result:
        logger.info(f"✅ Daisy voice test successful: {result}")
        return True, result
    else:
        logger.error("❌ Daisy voice test failed")
        return False, "Test failed"

def test_daisy_direct_generation():
    """Test direct Daisy voice generation without caching"""
    test_text = "This is a direct test of the Daisy Studious voice using the new TTS API."
    
    if not NEW_TTS_API_KEY or not NEW_TTS_API_URL:
        return False, "API not configured"
    
    try:
        url = f"{NEW_TTS_API_URL.rstrip('/')}/v1/text-to-speech"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {NEW_TTS_API_KEY}"
        }
        
        payload = {
            "text": test_text,
            "voice_id": DAISY_VOICE_ID,
            "model_id": NEW_TTS_MODEL_ID or "coqui"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            # Save test file
            test_filename = f"daisy_test_{timezone.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
            os.makedirs(tts_dir, exist_ok=True)
            test_filepath = os.path.join(tts_dir, test_filename)
            
            with open(test_filepath, 'wb') as f:
                f.write(response.content)
            
            if os.path.exists(test_filepath) and os.path.getsize(test_filepath) > 1000:
                media_url = f"/media/tts/{test_filename}"
                return True, media_url
            else:
                return False, "Generated file is empty"
        else:
            return False, f"API error: {response.status_code}"
            
    except Exception as e:
        return False, f"Test failed: {str(e)}"

def test_daisy_interview_simulation():
    """Test Daisy voice with interview-style questions"""
    questions = [
        "Welcome to your AI interview. Please introduce yourself.",
        "Can you tell me about your experience with Python programming?",
        "What interests you most about this position?"
    ]
    
    results = []
    for i, question in enumerate(questions, 1):
        logger.info(f"Testing question {i}: {question[:50]}...")
        result = generate_elevenlabs_tts(question, "female_interview")
        
        if result:
            results.append(f"Question {i}: ✅ {result}")
        else:
            results.append(f"Question {i}: ❌ Failed")
    
    return results

def generate_gtts_fallback(text):
    """Direct Google TTS fallback function"""
    return generate_google_tts(text)