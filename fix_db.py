#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("Running database fixes...")
    
    # Run migrations
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed")
    except Exception as e:
        print(f"❌ Migration error: {e}")
    
    # Run custom fix command
    try:
        execute_from_command_line(['manage.py', 'fix_interview_schema'])
        print("✅ Schema fix completed")
    except Exception as e:
        print(f"❌ Schema fix error: {e}")
    
    print("Database fix process completed")