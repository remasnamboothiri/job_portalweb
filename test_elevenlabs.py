#!/usr/bin/env python
"""
Quick test script to verify ElevenLabs TTS is working
Run this from the project directory: python test_elevenlabs.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.tts import generate_tts, generate_elevenlabs_tts, check_tts_system
from django.conf import settings

def test_elevenlabs():
    print("🔊 Testing ElevenLabs TTS Integration")
    print("=" * 50)
    
    # Check configuration
    api_key = getattr(settings, 'ELEVENLABS_API_KEY', '')
    print(f"API Key configured: {'✅ Yes' if api_key else '❌ No'}")
    
    if not api_key:
        print("❌ ElevenLabs API key not found in settings!")
        print("Make sure ELEVENLABS_API_KEY is set in your .env file")
        return False
    
    print(f"API Key (first 10 chars): {api_key[:10]}...")
    
    # Test system health
    print("\n🏥 System Health Check:")
    health = check_tts_system()
    for key, value in health.items():
        status = "✅" if value else "❌"
        print(f"  {key}: {status} {value}")
    
    # Test ElevenLabs directly
    print("\n🎤 Testing ElevenLabs TTS directly:")
    test_text = "Hello! I'm your AI interviewer. Welcome to your interview today."
    
    # Test all available voices
    from jobapp.tts import ELEVENLABS_VOICES
    print(f"\n📋 Available voices: {list(ELEVENLABS_VOICES.keys())}")
    
    result = generate_elevenlabs_tts(test_text, "female_professional")
    
    if result:
        print(f"✅ ElevenLabs TTS successful!")
        print(f"   Audio URL: {result}")
        
        # Check if file exists
        if result.startswith('/media/'):
            file_path = os.path.join(settings.MEDIA_ROOT, result.replace('/media/', ''))
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"   File exists: ✅ ({file_size} bytes)")
            else:
                print(f"   File exists: ❌ (path: {file_path})")
        
        return True
    else:
        print("❌ ElevenLabs TTS failed!")
        
        # Test fallback
        print("\n🔄 Testing gTTS fallback:")
        from jobapp.tts import generate_gtts_fallback
        fallback_result = generate_gtts_fallback(test_text)
        
        if fallback_result:
            print(f"✅ gTTS fallback works: {fallback_result}")
        else:
            print("❌ gTTS fallback also failed!")
        
        return False

def test_new_voice():
    print("\n🆕 Testing NEW voice (EaBs7G1VibMrNAuz2Na7):")
    test_text = "Hello! This is the new natural female voice. How does it sound?"
    
    result = generate_elevenlabs_tts(test_text, "female_natural")
    
    if result:
        print(f"✅ New voice test successful!")
        print(f"   Audio URL: {result}")
        return True
    else:
        print("❌ New voice test failed!")
        return False

def test_main_function():
    print("\n🎯 Testing main generate_tts function:")
    test_text = "This is a test of the main TTS function with female voice."
    
    result = generate_tts(test_text, model="female_professional")
    
    if result:
        print(f"✅ Main TTS function successful!")
        print(f"   Audio URL: {result}")
        
        # Determine which service was used
        if 'elevenlabs' in result:
            print("   🎤 Used: ElevenLabs (Premium)")
        elif 'gtts' in result:
            print("   🔊 Used: gTTS (Fallback)")
        else:
            print("   ❓ Used: Unknown service")
        
        return True
    else:
        print("❌ Main TTS function failed!")
        return False

if __name__ == "__main__":
    print("🚀 Starting ElevenLabs TTS Test")
    print("=" * 50)
    
    try:
        # Test ElevenLabs
        elevenlabs_success = test_elevenlabs()
        
        # Test new voice
        new_voice_success = test_new_voice()
        
        # Test main function
        main_success = test_main_function()
        
        print("\n" + "=" * 50)
        print("📊 Test Results:")
        print(f"ElevenLabs Direct: {'✅ PASS' if elevenlabs_success else '❌ FAIL'}")
        print(f"New Voice (female_natural): {'✅ PASS' if new_voice_success else '❌ FAIL'}")
        print(f"Main TTS Function: {'✅ PASS' if main_success else '❌ FAIL'}")
        
        if elevenlabs_success and new_voice_success and main_success:
            print("\n🎉 All tests passed! ElevenLabs TTS is working correctly.")
            print("Your interview system will now use high-quality female voice.")
        elif main_success:
            print("\n⚠️  Main function works but using fallback (gTTS).")
            print("Check your ElevenLabs API key and internet connection.")
        else:
            print("\n❌ Tests failed! Check your configuration.")
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()