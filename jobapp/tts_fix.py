# Quick TTS fix for network error issue
import os
import logging
from django.conf import settings
from gtts import gTTS
import hashlib

logger = logging.getLogger(__name__)

def generate_quick_tts(text):
    """Generate TTS quickly using only gTTS"""
    try:
        # Clean text
        clean_text = text.strip()[:500]  # Limit length
        if not clean_text:
            return None
            
        # Generate filename
        text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
        filename = f"quick_{text_hash}.mp3"
        
        # Create TTS directory
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        # Generate TTS
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(filepath)
        
        # Return media URL
        media_url = f"/media/tts/{filename}"
        logger.info(f"Quick TTS generated: {media_url}")
        return media_url
        
    except Exception as e:
        logger.error(f"Quick TTS failed: {e}")
        return None