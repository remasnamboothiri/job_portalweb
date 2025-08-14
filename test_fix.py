#!/usr/bin/env python
"""
Simple test script for the job portal database fixes
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

def main():
    print("Starting deployment fixes...")
    
    # 1. Test database connection
    print("\nTesting database connection...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("SUCCESS: Database connection working")
            else:
                print("ERROR: Database connection failed")
    except Exception as e:
        print(f"ERROR: Database connection error: {e}")
    
    # 2. Test Interview model
    print("\nTesting Interview model...")
    try:
        from jobapp.models import Interview
        
        # Try to get count without accessing problematic fields
        count = Interview.objects.count()
        print(f"SUCCESS: Found {count} interviews in database")
        
        # Test the safe property
        if count > 0:
            interview = Interview.objects.first()
            uuid_val = interview.get_uuid
            print(f"SUCCESS: Safe UUID access works: {uuid_val}")
        
    except Exception as e:
        print(f"ERROR: Interview model error: {e}")
    
    # 3. Run migrations
    print("\nRunning migrations...")
    try:
        from django.core.management import call_command
        call_command('migrate', verbosity=0)
        print("SUCCESS: Migrations completed")
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
    
    print("\nDeployment fix process completed!")

if __name__ == '__main__':
    main()