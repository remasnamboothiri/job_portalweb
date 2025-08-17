#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
    
    try:
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        
        print("=== Production Deployment ===")
        
        # 1. Fix duplicate UUIDs
        print("1. Fixing duplicate UUIDs...")
        execute_from_command_line(['manage.py', 'fix_duplicate_uuids'])
        
        # 2. Run migrations
        print("2. Running migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # 3. Collect static files
        print("3. Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        # 4. Test database
        print("4. Testing database...")
        execute_from_command_line(['manage.py', 'test_db'])
        
        print("=== Deployment Complete ===")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()