#!/usr/bin/env python3
"""
Simple test script to debug image upload issues
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.conf import settings
from jobapp.models import Job, CustomUser

def main():
    print("Testing Image Upload Functionality")
    print("=" * 40)
    
    # Check media settings
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    
    # Check if media directories exist
    media_root = settings.MEDIA_ROOT
    job_images_dir = os.path.join(media_root, 'job_images')
    
    print(f"Media root exists: {os.path.exists(media_root)}")
    print(f"Job images dir exists: {os.path.exists(job_images_dir)}")
    
    # Create directories if they don't exist
    if not os.path.exists(media_root):
        os.makedirs(media_root)
        print("Created media root directory")
    
    if not os.path.exists(job_images_dir):
        os.makedirs(job_images_dir)
        print("Created job_images directory")
    
    # Check existing jobs
    print("\nChecking existing jobs:")
    jobs = Job.objects.all()[:3]
    
    for job in jobs:
        print(f"\nJob: {job.title} (ID: {job.id})")
        print(f"  Image field: {job.featured_image}")
        
        if job.featured_image:
            print(f"  Image URL: {job.featured_image.url}")
            try:
                print(f"  Image path: {job.featured_image.path}")
                print(f"  File exists: {os.path.exists(job.featured_image.path)}")
                
                if os.path.exists(job.featured_image.path):
                    file_size = os.path.getsize(job.featured_image.path)
                    print(f"  File size: {file_size} bytes")
            except Exception as e:
                print(f"  Error accessing file: {e}")
        else:
            print("  No image")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()