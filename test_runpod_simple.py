#!/usr/bin/env python3
"""
Simple RunPod test - minimal code to test the API
"""

import os
import sys
import django
import requests

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.conf import settings

def test_runpod_simple():
    """Test RunPod API with minimal code"""
    
    RUNPOD_API_KEY = getattr(settings, 'RUNPOD_API_KEY', '')
    JWT_SECRET = getattr(settings, 'JWT_SECRET', '')
    
    print("🧪 SIMPLE RUNPOD TEST")
    print(f"API Key: {'✅ Present' if RUNPOD_API_KEY else '❌ Missing'}")
    print(f"JWT Secret: {'✅ Present' if JWT_SECRET else '❌ Missing'}")
    
    if not RUNPOD_API_KEY or not JWT_SECRET:
        print("❌ Missing credentials!")
        return
    
    # Test API call
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "text": "Hello, testing chatterbox female voice.",
            "model": "chatterbox",
            "voice_id": "female_default",
            "jwt_token": JWT_SECRET
        }
    }
    
    try:
        print("🚀 Making API call...")
        response = requests.post(
            "https://api.runpod.ai/v2/p3eso571qdfug9/runsync",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Response keys: {list(result.keys())}")
            
            if "output" in result:
                output = result["output"]
                if isinstance(output, dict) and "audio_base64" in output:
                    print(f"✅ Audio found! Length: {len(output['audio_base64'])}")
                else:
                    print(f"❌ No audio_base64 in output: {output}")
            else:
                print(f"❌ No output in response: {result}")
        else:
            print(f"❌ FAILED: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_runpod_simple()