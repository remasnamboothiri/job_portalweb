#!/usr/bin/env python3
"""
Test script to verify job editing functionality
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
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

def create_test_image(name="test_image.jpg"):
    """Create a test image file"""
    img = Image.new('RGB', (300, 200), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    return SimpleUploadedFile(
        name=name,
        content=img_io.getvalue(),
        content_type='image/jpeg'
    )

def test_job_edit():
    print("Testing Job Edit Functionality")
    print("=" * 40)
    
    # Find a job to edit
    job = Job.objects.first()
    if not job:
        print("No jobs found to test with")
        return
    
    print(f"Testing with job: {job.title} (ID: {job.id})")
    print(f"Current image: {job.featured_image}")
    
    # Create a new test image
    new_image = create_test_image("new_test_image.jpg")
    
    # Update the job with new image
    old_image_path = job.featured_image.path if job.featured_image else None
    
    job.featured_image = new_image
    job.save()
    
    print(f"Updated job image: {job.featured_image}")
    print(f"New image URL: {job.featured_image.url}")
    print(f"New image path: {job.featured_image.path}")
    
    # Check if file exists
    if os.path.exists(job.featured_image.path):
        file_size = os.path.getsize(job.featured_image.path)
        print(f"New image file size: {file_size} bytes")
        
        if file_size > 1000:  # Should be larger than placeholder
            print("SUCCESS: Image was properly uploaded!")
        else:
            print("WARNING: Image file seems too small")
    else:
        print("ERROR: Image file was not created")
    
    # Clean up old file if it existed
    if old_image_path and os.path.exists(old_image_path):
        try:
            os.remove(old_image_path)
            print("Cleaned up old image file")
        except:
            pass

if __name__ == "__main__":
    test_job_edit()