#!/usr/bin/env python3
"""
Fix missing job images by creating placeholder images or updating database
"""

import os
import sys
import django
from PIL import Image, ImageDraw, ImageFont

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.models import Job

def create_placeholder_image(image_path, text="Job Image"):
    """Create a placeholder image"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # Create a simple placeholder image
        img = Image.new('RGB', (800, 400), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (center)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (800 - text_width) // 2
        y = (400 - text_height) // 2
        
        # Draw text
        draw.text((x, y), text, fill='#666666', font=font)
        
        # Save image
        img.save(image_path, 'PNG')
        print(f"Created placeholder image: {image_path}")
        return True
        
    except Exception as e:
        print(f"Error creating placeholder image: {e}")
        return False

def fix_missing_images():
    """Fix all missing job images"""
    print("Checking for jobs with missing images...")
    
    jobs_with_images = Job.objects.exclude(featured_image='').exclude(featured_image__isnull=True)
    
    fixed_count = 0
    missing_count = 0
    
    for job in jobs_with_images:
        image_path = job.featured_image.path if job.featured_image else None
        
        if image_path and not os.path.exists(image_path):
            print(f"Missing image for job '{job.title}': {job.featured_image.name}")
            missing_count += 1
            
            # Option 1: Create placeholder image
            if create_placeholder_image(image_path, f"{job.title}\n{job.company}"):
                fixed_count += 1
                print(f"Fixed: {job.title}")
            
            # Option 2: Clear the image field (uncomment if you prefer this)
            # job.featured_image = None
            # job.save()
            # print(f"✅ Cleared image field for: {job.title}")
            # fixed_count += 1
    
    print(f"\nSummary:")
    print(f"   Missing images found: {missing_count}")
    print(f"   Images fixed: {fixed_count}")
    
    if missing_count == 0:
        print("No missing images found!")
    
    return fixed_count

def list_all_job_images():
    """List all job images in database"""
    print("All jobs with images:")
    jobs = Job.objects.exclude(featured_image='').exclude(featured_image__isnull=True)
    
    for job in jobs:
        exists = "OK" if os.path.exists(job.featured_image.path) else "MISSING"
        print(f"   {exists} {job.title}: {job.featured_image.name}")

if __name__ == "__main__":
    print("Job Image Fixer")
    print("=" * 50)
    
    # List current images
    list_all_job_images()
    print()
    
    # Fix missing images
    fixed = fix_missing_images()
    
    if fixed > 0:
        print(f"\nFixed {fixed} missing images!")
        print("Your job portal should now work without 404 errors.")
    
    print("\nDone!")