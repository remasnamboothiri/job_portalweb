#!/usr/bin/env python3
"""
Check what job images are referenced in the database
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.conf import settings
from jobapp.models import Job

def main():
    """Check job images in database vs filesystem"""
    
    print("Checking job images in database...")
    
    jobs = Job.objects.all()
    
    for job in jobs:
        print(f"\nJob: {job.title}")
        print(f"Company: {job.company}")
        
        if job.featured_image:
            image_path = str(job.featured_image)
            full_path = os.path.join(settings.MEDIA_ROOT, image_path)
            
            print(f"Database image path: {image_path}")
            print(f"Full filesystem path: {full_path}")
            print(f"File exists: {os.path.exists(full_path)}")
            
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                print(f"File size: {file_size} bytes")
                
                # Check if it's a real image or placeholder
                if file_size < 1000:  # Less than 1KB is likely placeholder
                    print("⚠️  This appears to be a placeholder file")
                else:
                    print("✅ This appears to be a real image file")
            else:
                print("❌ File missing from filesystem")
        else:
            print("No featured image set")
        
        print("-" * 50)

if __name__ == "__main__":
    main()