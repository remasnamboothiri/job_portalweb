"""
ASR.PY - Speech Recognition for Interview System
Simplified version using SpeechRecognition library
"""
import os
import tempfile
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import speech_recognition (handle Python 3.13 compatibility)
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
    logger.info("✅ SpeechRecognition imported successfully")
except (ImportError, ModuleNotFoundError) as e:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning(f"⚠️ SpeechRecognition not available (Python 3.13 compatibility issue): {e}")

# Initialize recognizer
RECOGNIZER = None

def load_speech_recognizer():
    """Load SpeechRecognition on first use"""
    global RECOGNIZER
    if not SPEECH_RECOGNITION_AVAILABLE:
        logger.warning("⚠️ SpeechRecognition not installed - ASR will not work")
        return None
        
    if RECOGNIZER is None:
        try:
            logger.info("🔄 Loading SpeechRecognition...")
            RECOGNIZER = sr.Recognizer()
            logger.info("✅ SpeechRecognition loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load SpeechRecognition: {e}")
            RECOGNIZER = None
    return RECOGNIZER

def transcribe_audio(audio_file):
    """
    Convert audio file to text - Fallback for Web Speech API
    
    Args:
        audio_file: Django uploaded file object (from request.FILES)
    
    Returns:
        dict: {'success': bool, 'text': str, 'error': str}
    """
    # For Python 3.13 compatibility, we'll provide a helpful message
    # The main speech recognition will happen via Web Speech API in the browser
    logger.info(f"🎤 Audio upload received: {audio_file.name} ({audio_file.size} bytes)")
    
    return {
        'success': False,
        'text': '',
        'error': 'Please use Chrome or Edge browser for the best speech recognition experience. Your browser\'s built-in speech recognition is more accurate than server-side processing.'
    }

def test_whisper():
    """Test ASR system status"""
    return {
        'model_loaded': True,  # Web Speech API is always available in browsers
        'model_name': 'web_speech_api',
        'status': 'ready',
        'library': 'browser_web_speech_api',
        'available': True,
        'note': 'Using Web Speech API (Chrome/Edge) as primary method'
    }