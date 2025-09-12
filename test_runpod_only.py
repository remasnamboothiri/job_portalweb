#!/usr/bin/env python3
"""
Test RunPod API only (no fallback to gTTS)
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.tts import generate_runpod_tts, RUNPOD_API_KEY, JWT_SECRET

def test_runpod_only():
    """Test RunPod API without any fallback"""
    
    print("=" * 60)
    print("RUNPOD ONLY TEST (NO FALLBACK)")
    print("=" * 60)
    
    print(f"API Key present: {bool(RUNPOD_API_KEY)}")
    print(f"JWT Secret present: {bool(JWT_SECRET)}")
    
    if not RUNPOD_API_KEY:
        print("❌ RUNPOD_API_KEY is missing!")
        print("Please set RUNPOD_API_KEY in your environment variables or Django settings.")
        return
    
    if not JWT_SECRET:
        print("❌ JWT_SECRET is missing!")
        print("Please set JWT_SECRET in your environment variables or Django settings.")
        return
    
    test_text = "Hello! I'm testing the chatterbox model with female default voice."
    
    print(f"\n🧪 Testing with text: '{test_text}'")
    print("-" * 40)
    
    try:
        result = generate_runpod_tts(test_text, "chatterbox")
        
        if result:
            print(f"✅ SUCCESS! Audio generated: {result}")
            
            # Check if file exists
            from django.conf import settings
            full_path = os.path.join(settings.BASE_DIR, result.lstrip('/'))
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                print(f"✅ File exists: {full_path}")
                print(f"✅ File size: {file_size} bytes")
                
                # Check file type
                if result.endswith('.mp3'):
                    print("✅ File type: MP3")
                elif result.endswith('.wav'):
                    print("✅ File type: WAV")
                else:
                    print(f"⚠️  Unknown file type: {result}")
            else:
                print(f"❌ File not found: {full_path}")
        else:
            print("❌ FAILED! No audio generated")
            print("This means the RunPod API call failed or returned no audio data.")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
    
    if not result:
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("1. Check your RUNPOD_API_KEY is correct")
        print("2. Check your JWT_SECRET is correct")
        print("3. Verify the RunPod endpoint is accessible")
        print("4. Check if the chatterbox model is available on your endpoint")
        print("5. Run the debug_runpod.py script for more detailed testing")

if __name__ == "__main__":
    test_runpod_only()