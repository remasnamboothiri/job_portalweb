#!/usr/bin/env python3
"""
Test real image upload by directly updating a job
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.models import Job
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

def create_real_test_image():
    """Create a real test image"""
    img = Image.new('RGB', (400, 300), color='green')
    # Add some text to make it identifiable
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try:
        # Try to use a default font
        font = ImageFont.load_default()
        draw.text((50, 150), "REAL UPLOAD TEST", fill='white', font=font)
    except:
        draw.text((50, 150), "REAL UPLOAD TEST", fill='white')
    
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    return SimpleUploadedFile(
        name="real_upload_test.jpg",
        content=img_io.getvalue(),
        content_type='image/jpeg'
    )

def main():
    print("Testing Real Image Upload")
    print("=" * 30)
    
    # Get the first job
    job = Job.objects.first()
    if not job:
        print("No jobs found")
        return
    
    print(f"Job: {job.title} (ID: {job.id})")
    print(f"Current image: {job.featured_image}")
    
    # Create and upload new image
    new_image = create_real_test_image()
    
    # Update the job
    job.featured_image = new_image
    job.save()
    
    print(f"Updated image: {job.featured_image}")
    print(f"Image URL: {job.featured_image.url}")
    
    # Verify file exists
    if os.path.exists(job.featured_image.path):
        file_size = os.path.getsize(job.featured_image.path)
        print(f"File size: {file_size} bytes")
        print("SUCCESS: Real upload test passed!")
    else:
        print("ERROR: File not found")

if __name__ == "__main__":
    main()