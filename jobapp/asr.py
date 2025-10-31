"""
ASR.PY - Speech Recognition for Interview System
Provides server-side speech-to-text as backup for Web Speech API
"""
import os
import tempfile
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import faster-whisper
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
    logger.info("✅ faster-whisper imported successfully")
except ImportError as e:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning(f"⚠️ faster-whisper not available: {e}")

# Load Whisper model (do this once when server starts)
WHISPER_MODEL = None

def load_whisper_model():
    """Load Faster Whisper model on first use"""
    global WHISPER_MODEL
    if not FASTER_WHISPER_AVAILABLE:
        logger.warning("⚠️ faster-whisper not installed - ASR will not work")
        return None
        
    if WHISPER_MODEL is None:
        try:
            # Use 'base' model for good balance of speed and accuracy
            # Model sizes: tiny, base, small, medium, large-v1, large-v2, large-v3
            logger.info("🔄 Loading Faster Whisper 'base' model...")
            WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
            logger.info("✅ Faster Whisper 'base' model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Faster Whisper model: {e}")
            WHISPER_MODEL = None
    return WHISPER_MODEL

def transcribe_audio(audio_file):
    """
    Convert audio file to text using Faster Whisper
    
    Args:
        audio_file: Django uploaded file object (from request.FILES)
    
    Returns:
        dict: {'success': bool, 'text': str, 'error': str}
    """
    model = load_whisper_model()
    if not model:
        return {
            'success': False,
            'text': '',
            'error': 'Faster Whisper model not available'
        }
    
    temp_file_path = None
    try:
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            # Write uploaded audio to temp file
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        logger.info(f"🎤 Transcribing audio file: {audio_file.name} ({audio_file.size} bytes)")
        
        # Transcribe using Faster Whisper
        segments, info = model.transcribe(temp_file_path, beam_size=5)
        
        # Combine all segments into one text
        transcribed_text = "".join([segment.text for segment in segments]).strip()
        
        if transcribed_text:
            logger.info(f"✅ Faster Whisper transcription successful: {transcribed_text[:50]}...")
            return {
                'success': True,
                'text': transcribed_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'text': '',
                'error': 'No speech detected in audio'
            }
            
    except Exception as e:
        logger.error(f"❌ Faster Whisper transcription failed: {e}")
        return {
            'success': False,
            'text': '',
            'error': str(e)
        }
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass

def test_whisper():
    """Test if Faster Whisper is working"""
    model = load_whisper_model()
    return {
        'model_loaded': model is not None,
        'model_name': 'base' if model else None,
        'status': 'ready' if model else 'not_loaded',
        'library': 'faster-whisper',
        'available': FASTER_WHISPER_AVAILABLE
    }