import requests
import os
from gtts import gTTS
from django.conf import settings
import uuid

def generate_tts(text, voice_id="female_default"):
    """
    Generate TTS audio with primary API and gTTS fallback
    """
    
    # Primary TTS API
    TTS_BASE_URL = "https://5s3w9bfsqpf5qb-8000.proxy.runpod.net"
    
    try:
        print(f"🔵 Sending TTS request to: {TTS_BASE_URL}/synthesize")
        
        payload = {
            'text': text,
            'voice_id': voice_id,
            'exaggeration': 0.5,
            'temperature': 0.3,
            'cfg_weight': 0.5,
            'seed': 0
        }
        
        print(f"📝 Payload: {payload}")
        
        # Step 1: Synthesize speech
        response = requests.post(
            f"{TTS_BASE_URL}/synthesize",
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {result}")
            
            if result.get('success') and result.get('audio_id'):
                audio_id = result['audio_id']
                
                # Step 2: Download audio using SAME base URL
                audio_url = f"{TTS_BASE_URL}/audio/{audio_id}"
                print(f"⬇️ Downloading audio from: {audio_url}")
                
                audio_response = requests.get(audio_url, timeout=30)
                
                if audio_response.status_code == 200:
                    # Save audio file
                    filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
                    filepath = os.path.join(settings.MEDIA_ROOT, 'tts', filename)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    with open(filepath, 'wb') as f:
                        f.write(audio_response.content)
                    
                    print(f"✅ Audio saved: {filepath}")
                    return f"/media/tts/{filename}"
                else:
                    print(f"❌ Failed to download audio: {audio_response.status_code}")
                    raise Exception(f"Audio download failed: {audio_response.status_code}")
            else:
                raise Exception("Invalid API response format")
        else:
            raise Exception(f"API request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Primary TTS failed: {e}")
        print("🔄 Using gTTS fallback...")
        
        # Fallback to gTTS
        return generate_gtts_fallback(text)

def generate_gtts_fallback(text):
    """
    Generate TTS using gTTS as fallback
    """
    try:
        filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(settings.MEDIA_ROOT, 'tts', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Generate gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filepath)
        
        print(f"✅ gTTS fallback successful: {filename}")
        return f"/media/tts/{filename}"
        
    except Exception as e:
        print(f"❌ gTTS fallback failed: {e}")
        return None

# Alias for backwards compatibility
generate_tts_audio = generate_tts