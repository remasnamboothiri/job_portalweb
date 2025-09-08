#!/usr/bin/env python3
"""
Final deployment script for media file fixes
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def check_files_exist():
    """Check if all required files exist"""
    print("\n📋 Checking required files...")
    
    required_files = [
        "media/job_images/ui-ux_designers_3h97VpP.webp",
        "media/job_images/magento_developer.jpg", 
        "media/job_images/python_django.png",
        "media/job_images/digital-marketing.webp",
        "media/job_images/devops.jpeg",
        "media/candidate_resumes/RAMA_S_NAMPOOTHIRY_CV.pdf",
        "static/images/hero_1.jpg",
        "static/fonts/icomoon/style.css",
        "static/fonts/line-icons/style.css"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Main deployment function"""
    print("🚀 Starting Media File Fix Deployment")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # 1. Check if files exist
    if not check_files_exist():
        print("\n⚠️  Some required files are missing!")
        print("Please run the fix scripts first:")
        print("1. python fix_media_files.py")
        print("2. python fix_template_static_paths.py")
        return False
    
    # 2. Git status
    print("\n📊 Checking Git status...")
    run_command("git status --porcelain", "Git status check")
    
    # 3. Add all changes
    if not run_command("git add .", "Adding all changes to Git"):
        return False
    
    # 4. Commit changes
    commit_message = """Fix: Resolve media file 404 errors and static file paths

- Create placeholder images for missing job images
- Create placeholder candidate resume  
- Fix static file paths in templates to use {% static %} tag
- Add {% load static %} to templates missing it
- Update login template font paths

Fixes the following 404 errors:
- /media/job_images/*.webp, *.jpg, *.png, *.jpeg
- /media/candidate_resumes/RAMA_S_NAMPOOTHIRY_CV.pdf
- /login/fonts/icomoon/style.css
- /login/fonts/line-icons/style.css
- /images/hero_1.jpg (incorrect path)"""
    
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("ℹ️  No changes to commit or commit failed")
    
    # 5. Push to origin
    if not run_command("git push origin main", "Pushing to remote repository"):
        print("⚠️  Push failed - check your Git configuration")
        return False
    
    # 6. Success message
    print("\n" + "=" * 50)
    print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    
    print("\n📋 What was fixed:")
    print("✅ Created placeholder media files")
    print("✅ Fixed static file paths in templates")
    print("✅ Added missing {% load static %} tags")
    print("✅ Committed and pushed all changes")
    
    print("\n🔍 Next Steps:")
    print("1. Wait for Render to deploy (2-3 minutes)")
    print("2. Test your application: https://job-portal-23qb.onrender.com")
    print("3. Check that no 404 errors appear in browser console")
    print("4. Verify images load on job dashboard")
    
    print("\n🌐 Test these URLs after deployment:")
    print("- https://job-portal-23qb.onrender.com/login/")
    print("- https://job-portal-23qb.onrender.com/dashboard/recruiter/")
    print("- https://job-portal-23qb.onrender.com/media/job_images/python_django.png")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)