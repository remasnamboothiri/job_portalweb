import requests
import os
import uuid
from django.conf import settings

def generate_tts(text):
    """
    Generate TTS audio using ChatterboxTTS API with gTTS fallback
    Returns the relative path to the audio file or None if failed
    """
    # Try external TTS first
    result = generate_external_tts(text)
    if result:
        return result
    
    # Fallback to gTTS
    print("🔄 External TTS failed, using gTTS fallback...")
    return generate_gtts_fallback(text)

def generate_external_tts(text):
    """Try external TTS service"""
    runpod_url = "https://srfh84s8etlw5u-8000.proxy.runpod.net/synthesize"
    
    # ✅ CORRECT PAYLOAD FORMAT - Simple dictionary with text
    payload = {
        "text": text,
        "voice_id": "female_default"  # Use a simple voice ID
    }
    
    try:
        print(f"🔵 Sending TTS request to: {runpod_url}")
        print(f"📝 Payload: {payload}")
        print(f"📝 Text to synthesize: '{text}'")
        
        # Send POST request
        response = requests.post(
            runpod_url, 
            json=payload,  # Send as JSON
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Response content: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Success! Response: {result}")
                
                # Look for audio URL or ID in different possible keys
                audio_url = None
                audio_id = None
                
                # Try different response key names
                possible_keys = ['audio_url', 'url', 'file_url', 'audio_id', 'id', 'audio_file']
                
                for key in possible_keys:
                    if key in result:
                        if 'url' in key or 'file' in key:
                            audio_url = result[key]
                            print(f"🔗 Found audio URL: {audio_url}")
                            break
                        elif 'id' in key:
                            audio_id = result[key]
                            # Construct URL using the audio ID
                            audio_url = f"https://srfh84s8etlw5u-8000.proxy.runpod.net/audio/{audio_id}"
                            print(f"🔗 Constructed audio URL from ID: {audio_url}")
                            break
                
                if audio_url:
                    # Download and save the audio file
                    return download_and_save_audio(audio_url)
                else:
                    print(f"❌ No audio URL found. Available keys: {list(result.keys())}")
                    return None
                    
            except Exception as e:
                print(f"❌ Error parsing JSON response: {e}")
                # Maybe it's direct audio content
                return save_direct_audio(response.content)
                
        elif response.status_code == 422:
            print("❌ 422 Error: Wrong payload format")
            print(f"📋 Error details: {response.text}")
            return None
        else:
            print(f"❌ TTS API Error: {response.status_code}")
            print(f"📋 Error response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ TTS request timed out")
        return None
    except Exception as e:
        print(f"❌ Exception in external TTS: {str(e)}")
        return None

def generate_gtts_fallback(text):
    """Fallback TTS using gTTS"""
    try:
        from gtts import gTTS
        import tempfile
        
        print(f"🔄 Using gTTS fallback for: '{text}'")
        
        # Create unique filename
        filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        
        # Ensure media directory exists
        media_dir = os.path.join(settings.BASE_DIR, "media", "tts")
        os.makedirs(media_dir, exist_ok=True)
        
        # Generate TTS
        tts = gTTS(text=text, lang='en', slow=False)
        audio_path = os.path.join(media_dir, filename)
        tts.save(audio_path)
        
        print(f"✅ gTTS fallback successful: {filename}")
        return f"/media/tts/{filename}"
        
    except Exception as e:
        print(f"❌ gTTS fallback failed: {e}")
        return None

def download_and_save_audio(audio_url):
    """Download audio from URL and save to local file"""
    try:
        print(f"⬇️ Downloading audio from: {audio_url}")
        
        audio_response = requests.get(audio_url, timeout=30)
        
        if audio_response.status_code == 200:
            return save_direct_audio(audio_response.content)
        else:
            print(f"❌ Failed to download audio: {audio_response.status_code}")
            print(f"❌ Download error: {audio_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading audio: {e}")
        return None

def save_direct_audio(audio_content):
    """Save audio content directly to file"""
    try:
        if not audio_content:
            print("❌ No audio content to save")
            return None
            
        # Create unique filename
        filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
        
        # Ensure media directory exists
        media_dir = os.path.join(settings.BASE_DIR, "media", "tts")
        os.makedirs(media_dir, exist_ok=True)
        
        # Save audio file
        audio_path = os.path.join(media_dir, filename)
        with open(audio_path, "wb") as f:
            f.write(audio_content)
        
        file_size = len(audio_content)
        print(f"✅ Audio saved successfully: {filename} ({file_size} bytes)")
        
        # Return the URL path for serving
        return f"/media/tts/{filename}"
        
    except Exception as e:
        print(f"❌ Error saving audio: {e}")
        return None



# import requests
# import os
# import uuid
# from django.conf import settings

# def generate_tts(text):
#     """
#     Generate TTS audio from text using RunPod endpoint
#     Returns the relative path to the audio file or None if failed
#     """
#     # ✅ CORRECTED: Proper API endpoint (replace with your actual endpoint)
#     runpod_url = "https://srfh84s8etlw5u-8000.proxy.runpod.net/synthesize"
#     # OR it might be:
#     # runpod_url = "https://srfh84s8etlw5u-8000.proxy.runpod.net/synthesize"
#     # OR: runpod_url = "https://srfh84s8etlw5u-8000.proxy.runpod.net/tts"
    
#     # ✅ SIMPLIFIED payload (adjust based on your TTS model requirements)
#     payload = {
#         "text": text,
#         "voice": "default",
#         "speed": 1.0
#     }
    
#     try:
#         print(f"🔵 Sending TTS request to: {runpod_url}")
#         print(f"📝 Text: {text}")
        
#         # Send request to RunPod
#         response = requests.post(runpod_url, json=payload, timeout=30)
        
#         print(f"📊 Response status: {response.status_code}")
        
#         if response.status_code == 200:
#             result = response.json()
#             print(f"📋 Response content: {result}")
            
#             # Handle different RunPod response formats
#             audio_url = None
#             if "output" in result:
#                 audio_url = result["output"]
#             elif "audio_url" in result:
#                 audio_url = result["audio_url"]
#             elif "url" in result:
#                 audio_url = result["url"]
#             elif "audio" in result:
#                 audio_url = result["audio"]
#             else:
#                 print("❌ Unexpected response format:", result)
#                 return None
            
#             print(f"🔗 Audio URL: {audio_url}")
            
#             # Download the audio file
#             audio_response = requests.get(audio_url, timeout=30)
#             if audio_response.status_code == 200:
#                 # Create unique filename
#                 filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
                
#                 # Ensure media directory exists
#                 media_dir = os.path.join(settings.BASE_DIR, "media", "tts")
#                 os.makedirs(media_dir, exist_ok=True)
                
#                 # Save audio file
#                 audio_path = os.path.join(media_dir, filename)
#                 with open(audio_path, "wb") as f:
#                     f.write(audio_response.content)
                
#                 file_size = len(audio_response.content)
#                 print(f"✅ Audio saved: {filename} ({file_size} bytes)")
                
#                 return f"/media/tts/{filename}"
#             else:
#                 print(f"❌ Failed to download audio: {audio_response.status_code}")
#                 return None
#         else:
#             print(f"❌ TTS API Error: {response.status_code}")
#             print(f"📋 Response: {response.text}")
#             return None
            
#     except requests.exceptions.Timeout:
#         print("❌ TTS request timed out")
#         return None
#     except Exception as e:
#         print(f"❌ Exception in TTS: {str(e)}")
#         return None