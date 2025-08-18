#!/usr/bin/env python
"""
Create migration for interview recording fields
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.core.management import execute_from_command_line

def create_recording_migration():
    """Create migration for interview recording fields"""
    try:
        print("🔄 Creating migration for interview recording fields...")
        
        # Create migration
        execute_from_command_line([
            'manage.py', 
            'makemigrations', 
            'jobapp',
            '--name', 
            'add_interview_recording_fields'
        ])
        
        print("✅ Migration created successfully!")
        print("📝 Run 'python manage.py migrate' to apply the migration")
        
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_recording_migration()