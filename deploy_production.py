#!/usr/bin/env python
"""
Production deployment script for job portal
Run this after deploying to production to fix database issues
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
import uuid

def main():
    print("🚀 Starting production deployment fixes...")
    
    try:
        # 1. Run migrations
        print("📦 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # 2. Fix database schema
        print("🔧 Fixing database schema...")
        execute_from_command_line(['manage.py', 'fix_production_db'])
        
        # 3. Collect static files
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        # 4. Test database
        print("🧪 Testing database...")
        execute_from_command_line(['manage.py', 'test_db'])
        
        print("✅ Production deployment completed successfully!")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()