#!/usr/bin/env python3
"""
Test script to simulate form-based image upload
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from jobapp.models import Job
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

def create_test_image():
    """Create a test image file"""
    img = Image.new('RGB', (300, 200), color='blue')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    return SimpleUploadedFile(
        name="test_form_image.jpg",
        content=img_io.getvalue(),
        content_type='image/jpeg'
    )

def test_form_upload():
    print("Testing Form-based Image Upload")
    print("=" * 40)
    
    User = get_user_model()
    
    # Find a recruiter user
    recruiter = User.objects.filter(is_recruiter=True).first()
    if not recruiter:
        print("No recruiter user found")
        return
    
    # Find a job to edit
    job = Job.objects.filter(posted_by=recruiter).first()
    if not job:
        print("No jobs found for recruiter")
        return
    
    print(f"Testing with job: {job.title} (ID: {job.id})")
    print(f"Current image: {job.featured_image}")
    
    # Create Django test client
    client = Client()
    
    # Login as recruiter
    client.force_login(recruiter)
    
    # Create test image
    test_image = create_test_image()
    
    # Prepare form data
    form_data = {
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'description': job.description,
        'department': job.department,
        'employment_type': job.employment_type,
        'experience_level': job.experience_level,
        'salary_min': job.salary_min,
        'salary_max': job.salary_max,
        'required_skills': job.required_skills,
        'status': job.status,
        'enable_ai_interview': job.enable_ai_interview,
        'featured_image': test_image,
    }
    
    print("Submitting form with image...")
    
    # Submit form
    response = client.post(f'/jobs/{job.id}/edit/', form_data)
    
    print(f"Response status: {response.status_code}")
    
    # Check if job was updated
    updated_job = Job.objects.get(id=job.id)
    print(f"Updated job image: {updated_job.featured_image}")
    
    if updated_job.featured_image and 'test_form_image' in str(updated_job.featured_image):
        print("SUCCESS: Form upload worked!")
        
        # Check file exists
        if os.path.exists(updated_job.featured_image.path):
            file_size = os.path.getsize(updated_job.featured_image.path)
            print(f"Image file size: {file_size} bytes")
        else:
            print("WARNING: Image file not found on disk")
    else:
        print("FAILED: Form upload did not work")
        
        if hasattr(response, 'content'):
            print(f"Response content: {response.content[:500]}")

if __name__ == "__main__":
    test_form_upload()