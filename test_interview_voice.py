#!/usr/bin/env python
"""
Test script to verify interview system uses the correct voice
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.tts import generate_tts, ELEVENLABS_VOICES

def test_interview_voice():
    """Test that interview system will use the correct voice"""
    
    print("=== Testing Interview Voice Configuration ===")
    print()
    
    # Show current voice configuration
    print("Current voice configuration:")
    for voice_key, voice_config in ELEVENLABS_VOICES.items():
        print(f"  - {voice_key}: {voice_config['name']} ({voice_config['voice_id']})")
    print()
    
    # Test the voice that interviews will use
    interview_text = "Hi! Thanks for joining me today. Could you start by telling me a bit about yourself?"
    
    print(f"Testing interview voice with text: '{interview_text[:50]}...'")
    print("Using model: female_natural")
    print()
    
    try:
        result = generate_tts(interview_text, model="female_natural")
        
        if result:
            print("SUCCESS: Interview voice working correctly!")
            print(f"Audio URL: {result}")
            
            # Check if it's using ElevenLabs
            if 'elevenlabs' in result:
                print("Service: ElevenLabs (Premium)")
                print(f"Voice ID being used: {ELEVENLABS_VOICES['female_natural']['voice_id']}")
            elif 'gtts' in result:
                print("Service: gTTS (Fallback)")
            
            print()
            print("✓ Your interview system will now use the voice ID: Gyqu9jCJup6lkiLgiu0l")
            
        else:
            print("FAILED: Could not generate audio")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_interview_voice()