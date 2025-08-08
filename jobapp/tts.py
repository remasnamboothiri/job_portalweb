import requests
import os
from gtts import gTTS
from django.conf import settings
import uuid
import tempfile

def generate_tts(text, voice_id="female_default"):
    """
    Generate TTS audio with primary API and gTTS fallback
    Enhanced with better error handling and logging
    """
    
    # FIXED: Correct API base URL (remove /docs/)
    TTS_BASE_URL = "https://56kz529ck8vq9d-8000.proxy.runpod.net"
    
    try:
        print(f"🔵 Starting TTS generation for: '{text[:50]}...'")
        print(f"🔵 Using API URL: {TTS_BASE_URL}")
        
        payload = {
            'text': text,
            'voice_id': voice_id,
            'exaggeration': 0.5,
            'temperature': 0.3,
            'cfg_weight': 0.5,
            'seed': 0
        }
        
        print(f"📝 Request payload: {payload}")
        
        # Step 1: Synthesize speech
        synthesize_url = f"{TTS_BASE_URL}/synthesize"
        print(f"📤 Sending POST request to: {synthesize_url}")
        
        response = requests.post(
            synthesize_url,
            json=payload,
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ API Response: {result}")
                
                if result.get('success') and result.get('audio_id'):
                    audio_id = result['audio_id']
                    print(f"🎵 Audio ID received: {audio_id}")
                    
                    # Step 2: Download audio using corrected URL
                    audio_url = f"{TTS_BASE_URL}/audio/{audio_id}"
                    print(f"⬇️ Downloading audio from: {audio_url}")
                    
                    audio_response = requests.get(audio_url, timeout=30)
                    print(f"📊 Audio download status: {audio_response.status_code}")
                    
                    if audio_response.status_code == 200:
                        content_length = len(audio_response.content)
                        print(f"📦 Audio content length: {content_length} bytes")
                        
                        if content_length == 0:
                            print(f"❌ Audio content is empty")
                            raise Exception("Downloaded audio file is empty")
                        
                        # Save audio file
                        filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
                        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
                        os.makedirs(tts_dir, exist_ok=True)
                        filepath = os.path.join(tts_dir, filename)
                        
                        print(f"💾 Saving audio to: {filepath}")
                        
                        with open(filepath, 'wb') as f:
                            f.write(audio_response.content)
                        
                        # Verify file was created and has content
                        if os.path.exists(filepath):
                            file_size = os.path.getsize(filepath)
                            print(f"✅ Audio file saved successfully: {filepath}")
                            print(f"📁 File size: {file_size} bytes")
                            
                            if file_size > 0:
                                media_url = f"/media/tts/{filename}"
                                print(f"🌐 Media URL: {media_url}")
                                return media_url
                            else:
                                print(f"❌ Saved file is empty")
                                os.remove(filepath)  # Clean up empty file
                                raise Exception("Saved audio file is empty")
                        else:
                            print(f"❌ File was not created: {filepath}")
                            raise Exception("Audio file was not created")
                            
                    else:
                        print(f"❌ Failed to download audio: {audio_response.status_code}")
                        print(f"❌ Audio response content: {audio_response.text[:200]}...")
                        raise Exception(f"Audio download failed with status {audio_response.status_code}")
                        
                else:
                    print(f"❌ Invalid API response structure: {result}")
                    if 'error' in result:
                        print(f"❌ API Error: {result['error']}")
                    raise Exception("API returned invalid response structure")
                    
            except ValueError as json_error:
                print(f"❌ JSON decode error: {json_error}")
                print(f"❌ Raw response content: {response.text[:200]}...")
                raise Exception(f"Invalid JSON response: {json_error}")
                
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            print(f"❌ Response content: {response.text[:200]}...")
            
            # Try to parse error message
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"❌ API Error detail: {error_data['detail']}")
            except:
                pass
                
            raise Exception(f"API request failed with status {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout after 30 seconds")
        print("🔄 Falling back to gTTS...")
        return generate_gtts_fallback(text)
        
    except requests.exceptions.ConnectionError as conn_error:
        print(f"❌ Connection error: {conn_error}")
        print("🔄 Falling back to gTTS...")
        return generate_gtts_fallback(text)
        
    except Exception as e:
        print(f"❌ Primary TTS failed: {type(e).__name__}: {e}")
        print("🔄 Falling back to gTTS...")
        return generate_gtts_fallback(text)

def generate_gtts_fallback(text):
    """
    Generate TTS using gTTS as fallback with enhanced error handling
    """
    try:
        print(f"🔄 Starting gTTS fallback for: '{text[:50]}...'")
        
        # Clean text for gTTS
        clean_text = text.strip()
        if not clean_text:
            print(f"❌ Empty text provided to gTTS")
            return None
            
        if len(clean_text) > 5000:  # gTTS has character limits
            clean_text = clean_text[:5000]
            print(f"⚠️ Text truncated to 5000 characters for gTTS")
        
        filename = f"gtts_{uuid.uuid4().hex[:8]}.mp3"
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        print(f"🗣️ Generating gTTS audio...")
        
        # Generate gTTS with error handling
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(filepath)
        
        # Verify file was created and has content
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✅ gTTS file created: {filepath}")
            print(f"📁 File size: {file_size} bytes")
            
            if file_size > 0:
                media_url = f"/media/tts/{filename}"
                print(f"🌐 gTTS Media URL: {media_url}")
                return media_url
            else:
                print(f"❌ gTTS file is empty")
                os.remove(filepath)  # Clean up empty file
                return None
        else:
            print(f"❌ gTTS file was not created")
            return None
            
    except Exception as e:
        print(f"❌ gTTS fallback also failed: {type(e).__name__}: {e}")
        return None

def test_tts_generation(test_text=None):
    """
    Test function to debug TTS generation
    """
    if test_text is None:
        test_text = "Hello, this is a test of the text to speech system. Can you hear me clearly?"
    
    print(f"🧪 Testing TTS with text: '{test_text}'")
    
    # Test primary TTS
    print(f"🧪 Testing primary TTS API...")
    result = generate_tts(test_text)
    
    if result:
        print(f"✅ TTS test successful: {result}")
        
        # Verify file exists
        import os
        from django.conf import settings
        full_path = os.path.join(settings.BASE_DIR, result.lstrip('/'))
        if os.path.exists(full_path):
            print(f"✅ File verified at: {full_path}")
            print(f"📁 File size: {os.path.getsize(full_path)} bytes")
        else:
            print(f"❌ File not found at: {full_path}")
    else:
        print(f"❌ TTS test failed")
    
    return result

def cleanup_old_tts_files(days_old=1):
    """
    Clean up TTS files older than specified days
    """
    try:
        import time
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        if not os.path.exists(tts_dir):
            return
            
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        cleaned_count = 0
        for filename in os.listdir(tts_dir):
            filepath = os.path.join(tts_dir, filename)
            if os.path.isfile(filepath):
                file_modified = os.path.getmtime(filepath)
                if file_modified < cutoff_time:
                    os.remove(filepath)
                    cleaned_count += 1
                    
        print(f"🧹 Cleaned up {cleaned_count} old TTS files")
        
    except Exception as e:
        print(f"❌ TTS cleanup failed: {e}")

# Alias for backwards compatibility
generate_tts_audio = generate_tts

# Debug function to check TTS system health
def check_tts_system():
    """
    Check TTS system health and configuration
    """
    from django.conf import settings
    
    health_info = {
        'media_root': settings.MEDIA_ROOT,
        'media_url': settings.MEDIA_URL,
        'tts_dir_exists': os.path.exists(os.path.join(settings.MEDIA_ROOT, 'tts')),
        'tts_api_url': "https://56kz529ck8vq9d-8000.proxy.runpod.net",
    }
    
    # Check if we can create TTS directory
    try:
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        health_info['can_create_tts_dir'] = True
    except Exception as e:
        health_info['can_create_tts_dir'] = False
        health_info['tts_dir_error'] = str(e)
    
    # Test gTTS availability
    try:
        from gtts import gTTS
        health_info['gtts_available'] = True
    except ImportError as e:
        health_info['gtts_available'] = False
        health_info['gtts_error'] = str(e)
    
    # Check network connectivity to TTS API
    try:
        response = requests.get("https://56kz529ck8vq9d-8000.proxy.runpod.net", timeout=5)
        health_info['api_reachable'] = True
        health_info['api_status'] = response.status_code
    except Exception as e:
        health_info['api_reachable'] = False
        health_info['api_error'] = str(e)
    
    print("🏥 TTS System Health Check:")
    for key, value in health_info.items():
        print(f"   {key}: {value}")
    
    return health_info