#!/usr/bin/env python
"""
Test script to verify TTS system after ElevenLabs fix
Run this after updating your API key
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.tts import generate_tts, check_tts_system, generate_elevenlabs_tts, generate_gtts_fallback

def test_tts_system():
    """Test the TTS system with different methods"""
    
    test_text = "Hello, this is a test of the female voice for job interviews. Can you hear me clearly?"
    
    print("🔧 Testing TTS System...")
    print("=" * 50)
    
    # 1. System health check
    print("1. System Health Check:")
    health = check_tts_system()
    for key, value in health.items():
        print(f"   {key}: {value}")
    print()
    
    # 2. Test ElevenLabs directly
    print("2. Testing ElevenLabs (female_interview):")
    elevenlabs_result = generate_elevenlabs_tts(test_text, "female_interview")
    if elevenlabs_result:
        print(f"   ✅ ElevenLabs SUCCESS: {elevenlabs_result}")
    else:
        print("   ❌ ElevenLabs FAILED")
    print()
    
    # 3. Test gTTS fallback
    print("3. Testing gTTS Fallback:")
    gtts_result = generate_gtts_fallback(test_text)
    if gtts_result:
        print(f"   ✅ gTTS SUCCESS: {gtts_result}")
    else:
        print("   ❌ gTTS FAILED")
    print()
    
    # 4. Test main TTS function
    print("4. Testing Main TTS Function:")
    main_result = generate_tts(test_text, "female_interview")
    if main_result:
        print(f"   ✅ Main TTS SUCCESS: {main_result}")
        if "elevenlabs" in main_result:
            print("   🎉 Using ElevenLabs (Primary)")
        elif "gtts" in main_result:
            print("   ⚠️  Using gTTS (Fallback)")
    else:
        print("   ❌ Main TTS FAILED")
    print()
    
    # 5. Summary
    print("=" * 50)
    if main_result:
        print("🎉 TTS SYSTEM IS WORKING!")
        if "elevenlabs" in main_result:
            print("✅ ElevenLabs female voice is working perfectly!")
        else:
            print("⚠️  Using gTTS fallback - consider fixing ElevenLabs API key")
    else:
        print("❌ TTS SYSTEM FAILED - Check your configuration")
    
    return main_result

if __name__ == "__main__":
    test_tts_system()