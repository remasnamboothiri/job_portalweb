#!/usr/bin/env python3
"""
Debug script to test RunPod API directly
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.conf import settings

def test_runpod_api():
    """Test RunPod API directly with different payload formats"""
    
    RUNPOD_API_KEY = getattr(settings, 'RUNPOD_API_KEY', '')
    JWT_SECRET = getattr(settings, 'JWT_SECRET', '')
    RUNPOD_ENDPOINT = "https://api.runpod.ai/v2/p3eso571qdfug9/runsync"
    
    print("=" * 60)
    print("RUNPOD API DEBUG TEST")
    print("=" * 60)
    
    print(f"API Key present: {bool(RUNPOD_API_KEY)}")
    print(f"JWT Secret present: {bool(JWT_SECRET)}")
    print(f"Endpoint: {RUNPOD_ENDPOINT}")
    print()
    
    if not RUNPOD_API_KEY or not JWT_SECRET:
        print("❌ Missing API credentials!")
        return
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test different payload formats
    test_payloads = [
        {
            "name": "Chatterbox with female_default",
            "payload": {
                "input": {
                    "text": "Hello, this is a test of the chatterbox model with female default voice.",
                    "model": "chatterbox",
                    "voice_id": "female_default",
                    "jwt_token": JWT_SECRET
                }
            }
        },
        {
            "name": "Simple chatterbox",
            "payload": {
                "input": {
                    "text": "Hello, testing chatterbox model.",
                    "model": "chatterbox",
                    "jwt_token": JWT_SECRET
                }
            }
        },
        {
            "name": "Original kokkoro format",
            "payload": {
                "input": {
                    "text": "Hello, testing original format.",
                    "voice_id": "kokkoro",
                    "jwt_token": JWT_SECRET
                }
            }
        }
    ]
    
    for test in test_payloads:
        print(f"\n🧪 Testing: {test['name']}")
        print("-" * 40)
        print(f"Payload: {json.dumps(test['payload'], indent=2)}")
        
        try:
            response = requests.post(
                RUNPOD_ENDPOINT,
                headers=headers,
                json=test['payload'],
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"✅ SUCCESS!")
                    print(f"Response keys: {list(result.keys())}")
                    
                    if "output" in result:
                        output = result["output"]
                        print(f"Output type: {type(output)}")
                        if isinstance(output, dict):
                            print(f"Output keys: {list(output.keys())}")
                            
                            # Check for audio data
                            if "audio_base64" in output:
                                print(f"✅ Found audio_base64 (length: {len(output['audio_base64'])})")
                            elif "audio_data" in output:
                                print(f"✅ Found audio_data (length: {len(output['audio_data'])})")
                            else:
                                print("❌ No audio data found in output")
                                print(f"Available fields: {list(output.keys())}")
                        else:
                            print(f"Output content: {output}")
                    else:
                        print("❌ No 'output' field in response")
                        print(f"Available fields: {list(result.keys())}")
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {response.text}")
            else:
                print(f"❌ FAILED with status {response.status_code}")
                print(f"Error response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("DEBUG TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_runpod_api()