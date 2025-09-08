#!/usr/bin/env python3
"""
Test script to debug image upload issues
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

def test_image_upload():
    """Test image upload functionality"""
    print("Testing Image Upload Functionality")
    print("=" * 50)
    
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
    
    # Check for a recruiter user
    try:
        recruiter = CustomUser.objects.filter(is_recruiter=True).first()
        if not recruiter:
            print("❌ No recruiter user found. Please create one first.")
            return
        
        print(f"👤 Found recruiter: {recruiter.username}")
        
        # Create a test image
        print("🖼️ Creating test image...")
        img = Image.new('RGB', (300, 200), color='lightblue')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        # Create uploaded file object
        test_image = SimpleUploadedFile(
            name='test_job_image.jpg',
            content=img_io.getvalue(),
            content_type='image/jpeg'
        )
        
        # Create a test job with image
        test_job = Job.objects.create(
            title="TEST IMAGE UPLOAD JOB - DELETE ME",
            company="Test Company",
            location="Test Location",
            description="This is a test job to verify image upload functionality. Please delete after testing.",
            posted_by=recruiter,
            featured_image=test_image
        )
        
        print(f"✅ Created test job with ID: {test_job.id}")
        print(f"🖼️ Image field value: {test_job.featured_image}")
        print(f"🖼️ Image URL: {test_job.featured_image.url if test_job.featured_image else 'None'}")
        
        # Check if file was actually saved
        if test_job.featured_image:
            image_path = test_job.featured_image.path
            print(f"📁 Image file path: {image_path}")
            print(f"📁 Image file exists: {os.path.exists(image_path)}")
            
            if os.path.exists(image_path):
                file_size = os.path.getsize(image_path)
                print(f"📏 Image file size: {file_size} bytes")
                
                if file_size > 0:
                    print("✅ Image upload test PASSED!")
                else:
                    print("❌ Image file is empty")
            else:
                print("❌ Image file was not saved to disk")
        else:
            print("❌ No image was saved to the job")
        
        # Test job retrieval
        retrieved_job = Job.objects.get(id=test_job.id)
        print(f"🔍 Retrieved job image: {retrieved_job.featured_image}")
        
        # Clean up
        print("\n🧹 Cleaning up test job...")
        test_job.delete()
        print("✅ Test job deleted")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

def check_existing_jobs():
    """Check existing jobs and their images"""
    print("\n🔍 Checking Existing Jobs")
    print("=" * 30)
    
    jobs = Job.objects.all()[:5]  # Check first 5 jobs
    
    for job in jobs:
        print(f"\n📋 Job: {job.title}")
        print(f"   ID: {job.id}")
        print(f"   Image field: {job.featured_image}")
        
        if job.featured_image:
            print(f"   Image URL: {job.featured_image.url}")
            print(f"   Image path: {job.featured_image.path}")
            print(f"   File exists: {os.path.exists(job.featured_image.path)}")
            
            if os.path.exists(job.featured_image.path):
                file_size = os.path.getsize(job.featured_image.path)
                print(f"   File size: {file_size} bytes")
        else:
            print("   No image")

if __name__ == "__main__":
    test_image_upload()
    check_existing_jobs()