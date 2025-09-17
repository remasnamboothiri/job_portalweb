#!/usr/bin/env python
"""
Direct test of ElevenLabs API to debug the issue
"""

import requests
import os

# Your credentials
API_KEY = "sk_fc0d2f20d3c7779c47f2719251eadbdfffdd091553d1bec7"
VOICE_ID = "i4CzbCVWoqvD0P1QJCUL"
API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

def test_elevenlabs_direct():
    """Test ElevenLabs API directly"""
    
    print("Testing ElevenLabs API directly...")
    print(f"API Key: {API_KEY[:20]}...")
    print(f"Voice ID: {VOICE_ID}")
    print(f"URL: {API_URL}")
    print("=" * 50)
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    
    payload = {
        "text": "Hello, this is a test of your ElevenLabs voice for interviews.",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    try:
        print("Making API request...")
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("SUCCESS! ElevenLabs API is working")
            print(f"Audio size: {len(response.content)} bytes")
            
            # Save test file
            with open("test_elevenlabs_output.mp3", "wb") as f:
                f.write(response.content)
            print("Test audio saved as 'test_elevenlabs_output.mp3'")
            
        else:
            print("FAILED!")
            print(f"Error Response: {response.text}")
            
            # Specific error analysis
            if response.status_code == 401:
                print("DIAGNOSIS: Invalid API key or unauthorized")
            elif response.status_code == 422:
                print("DIAGNOSIS: Invalid voice ID or request format")
            elif response.status_code == 429:
                print("DIAGNOSIS: Rate limit exceeded")
            else:
                print(f"DIAGNOSIS: Unknown error {response.status_code}")
                
    except Exception as e:
        print(f"REQUEST FAILED: {e}")

if __name__ == "__main__":
    test_elevenlabs_direct()