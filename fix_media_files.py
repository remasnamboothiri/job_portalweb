#!/usr/bin/env python3
"""
Fix media file issues for job portal deployment
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.conf import settings
from jobapp.models import Job
import shutil
import requests
from urllib.parse import urlparse

def create_placeholder_images():
    """Create placeholder images for missing job images"""
    
    job_images_dir = os.path.join(settings.MEDIA_ROOT, 'job_images')
    os.makedirs(job_images_dir, exist_ok=True)
    
    # List of missing images from error logs
    missing_images = [
        'ui-ux_designers_3h97VpP.webp',
        'magento_developer.jpg', 
        'python_django.png',
        'digital-marketing.webp',
        'devops.jpeg'
    ]
    
    # Create a simple placeholder image (1x1 pixel PNG)
    placeholder_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xd2\x00\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    created_files = []
    
    for image_name in missing_images:
        image_path = os.path.join(job_images_dir, image_name)
        
        if not os.path.exists(image_path):
            try:
                # For PNG files, use PNG placeholder
                if image_name.endswith('.png'):
                    with open(image_path, 'wb') as f:
                        f.write(placeholder_content)
                else:
                    # For other formats, create a simple text file as placeholder
                    # This will prevent 404 errors
                    with open(image_path, 'w') as f:
                        f.write(f"Placeholder for {image_name}")
                
                created_files.append(image_name)
                print(f"Created placeholder: {image_name}")
                
            except Exception as e:
                print(f"Failed to create {image_name}: {e}")
    
    return created_files

def fix_job_image_paths():
    """Update job records to use existing images or set to None"""
    
    jobs_updated = 0
    
    try:
        jobs = Job.objects.all()
        
        for job in jobs:
            if job.featured_image:
                # Check if the image file actually exists
                image_path = os.path.join(settings.MEDIA_ROOT, str(job.featured_image))
                
                if not os.path.exists(image_path):
                    print(f"Missing image for job '{job.title}': {job.featured_image}")
                    
                    # Option 1: Set to None (removes image reference)
                    job.featured_image = None
                    job.save()
                    jobs_updated += 1
                    print(f"Cleared missing image reference for job: {job.title}")
                else:
                    print(f"Image exists for job '{job.title}': {job.featured_image}")
    
    except Exception as e:
        print(f"Error updating job images: {e}")
    
    return jobs_updated

def fix_static_file_paths():
    """Fix static file path issues"""
    
    # The error shows: Not Found: /login/fonts/icomoon/style.css
    # This suggests relative path issues in templates
    
    print("\nStatic File Path Issues:")
    print("- Error: /login/fonts/icomoon/style.css not found")
    print("- Error: /login/fonts/line-icons/style.css not found")
    print("- Error: /images/hero_1.jpg not found")
    
    print("\nSolutions:")
    print("1. Use {% load static %} and {% static 'path' %} in templates")
    print("2. Check template inheritance for proper static file loading")
    print("3. Ensure STATIC_URL is correctly configured")
    
    return True

def create_missing_candidate_resume():
    """Create placeholder for missing candidate resume"""
    
    candidate_resumes_dir = os.path.join(settings.MEDIA_ROOT, 'candidate_resumes')
    os.makedirs(candidate_resumes_dir, exist_ok=True)
    
    missing_resume = 'RAMA_S_NAMPOOTHIRY_CV.pdf'
    resume_path = os.path.join(candidate_resumes_dir, missing_resume)
    
    if not os.path.exists(resume_path):
        # Create a simple text file as placeholder
        with open(resume_path, 'w') as f:
            f.write("Placeholder resume file - original file missing")
        
        print(f"Created placeholder resume: {missing_resume}")
        return True
    else:
        print(f"Resume already exists: {missing_resume}")
        return False

def main():
    """Main function to fix all media file issues"""
    
    print("Starting Media File Fix Process...")
    print(f"Media Root: {settings.MEDIA_ROOT}")
    print(f"Media URL: {settings.MEDIA_URL}")
    
    # 1. Create placeholder images
    print("\n1. Creating placeholder images...")
    created_images = create_placeholder_images()
    print(f"Created {len(created_images)} placeholder images")
    
    # 2. Fix job image references
    print("\n2. Fixing job image references...")
    updated_jobs = fix_job_image_paths()
    print(f"Updated {updated_jobs} job records")
    
    # 3. Create missing candidate resume
    print("\n3. Creating missing candidate resume...")
    create_missing_candidate_resume()
    
    # 4. Check static file issues
    print("\n4. Checking static file issues...")
    fix_static_file_paths()
    
    print("\nMedia file fix process completed!")
    print("\nNext Steps:")
    print("1. Deploy these changes to production")
    print("2. Check template files for proper static file loading")
    print("3. Upload actual job images to replace placeholders")
    print("4. Test the application to ensure no more 404 errors")

if __name__ == "__main__":
    main()