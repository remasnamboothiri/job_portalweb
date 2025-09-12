#!/usr/bin/env python3
"""
Test script to verify chatterbox model configuration with female_default voice
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.tts import (
    AVAILABLE_VOICES, 
    BUILTIN_VOICES, 
    generate_tts, 
    test_chatterbox_voice,
    check_tts_system
)

def test_configuration():
    """Test the updated TTS configuration"""
    print("=" * 60)
    print("CHATTERBOX MODEL CONFIGURATION TEST")
    print("=" * 60)
    
    # Test 1: Check available voices
    print("\n1. Available Voices Configuration:")
    print("-" * 40)
    for voice_name, config in AVAILABLE_VOICES.items():
        print(f"Voice: {voice_name}")
        print(f"  - Voice ID: {config.get('voice_id')}")
        print(f"  - Name: {config.get('name')}")
        print(f"  - Description: {config.get('description')}")
        print(f"  - Type: {config.get('type')}")
        print(f"  - Model: {config.get('model', 'N/A')}")
        print()
    
    # Test 2: Check builtin voices
    print("2. Builtin Voices Configuration:")
    print("-" * 40)
    for voice_name, config in BUILTIN_VOICES.items():
        print(f"Voice: {voice_name}")
        print(f"  - Voice ID: {config.get('voice_id')}")
        print(f"  - Name: {config.get('name')}")
        print(f"  - Description: {config.get('description')}")
        print(f"  - Audio URL: {config.get('audio_url')}")
        print(f"  - Type: {config.get('type')}")
        print(f"  - Created At: {config.get('created_at')}")
        print()
    
    # Test 3: System health check
    print("3. TTS System Health Check:")
    print("-" * 40)
    try:
        health_info = check_tts_system()
        for key, value in health_info.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"  Health check failed: {e}")
    
    # Test 4: Test chatterbox voice generation
    print("\n4. Testing Chatterbox Voice Generation:")
    print("-" * 40)
    test_text = "Hello! I'm your AI interviewer using the female default voice from the chatterbox model."
    
    try:
        print(f"Testing with text: '{test_text}'")
        result = test_chatterbox_voice(test_text)
        if result:
            print(f"✅ SUCCESS: Audio generated at {result}")
        else:
            print("❌ FAILED: No audio generated")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 5: Test regular TTS with chatterbox model
    print("\n5. Testing Regular TTS with Chatterbox Model:")
    print("-" * 40)
    try:
        result = generate_tts(test_text, model="chatterbox")
        if result:
            print(f"✅ SUCCESS: Audio generated at {result}")
        else:
            print("❌ FAILED: No audio generated")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("CONFIGURATION TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_configuration()