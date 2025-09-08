#!/usr/bin/env python3
"""
Create proper placeholder images for job postings
"""

import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_placeholder_image(filename, text):
    """Create a placeholder image with text"""
    
    # Create image
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw border
    draw.rectangle([10, 10, width-10, height-10], outline='#cccccc', width=2)
    
    # Draw main text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 20
    
    draw.text((x, y), text, fill='#666666', font=font)
    
    # Draw subtitle
    subtitle = "Upload actual image when posting job"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=small_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    
    x_sub = (width - subtitle_width) // 2
    y_sub = y + text_height + 10
    
    draw.text((x_sub, y_sub), subtitle, fill='#999999', font=small_font)
    
    return image

def main():
    """Create placeholder images for missing job images"""
    
    # Ensure directory exists
    job_images_dir = Path("media/job_images")
    job_images_dir.mkdir(parents=True, exist_ok=True)
    
    # Job categories and their images
    placeholders = {
        'python_django.png': 'Python Django',
        'devops.jpeg': 'DevOps Engineer', 
        'ui-ux_designers_3h97VpP.webp': 'UI/UX Designer',
        'digital-marketing.webp': 'Digital Marketing',
        'magento_developer.jpg': 'Magento Developer'
    }
    
    created_count = 0
    
    for filename, job_type in placeholders.items():
        filepath = job_images_dir / filename
        
        try:
            # Create placeholder image
            image = create_placeholder_image(job_type, job_type)
            
            # Save as PNG regardless of extension (for compatibility)
            image.save(filepath, 'PNG')
            
            print(f"Created placeholder: {filename}")
            created_count += 1
            
        except Exception as e:
            print(f"Error creating {filename}: {e}")
    
    print(f"\nCreated {created_count} placeholder images")
    print("\nThese are temporary placeholders.")
    print("When you post new jobs in production, upload actual images.")

if __name__ == "__main__":
    main()