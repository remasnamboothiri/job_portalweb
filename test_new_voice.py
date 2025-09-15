#!/usr/bin/env python
"""
Test script for the new ElevenLabs voice ID: EaBs7G1VibMrNAuz2Na7
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.tts import generate_tts, ELEVENLABS_VOICES, AVAILABLE_VOICES

def test_new_voice():
    """Test the new female_natural voice"""
    
    print("=== Testing New ElevenLabs Voice ===")
    print(f"Voice ID: EaBs7G1VibMrNAuz2Na7")
    print()
    
    # Display all available voices
    print("Available voices:")
    for voice_key, voice_config in ELEVENLABS_VOICES.items():
        print(f"  - {voice_key}: {voice_config['name']} ({voice_config['voice_id']})")
    print()
    
    # Test the new voice
    test_text = "Hello! This is a test of the new natural female voice. How does it sound?"
    
    print(f"Testing with text: '{test_text}'")
    print("Generating audio with female_natural voice...")
    
    try:
        result = generate_tts(test_text, model="female_natural")
        
        if result:
            print("SUCCESS: Audio generated successfully!")
            print(f"Audio URL: {result}")
        else:
            print("FAILED: Could not generate audio")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_new_voice()