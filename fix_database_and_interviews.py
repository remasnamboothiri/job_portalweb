#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def fix_everything():
    print("🔧 FIXING DATABASE AND INTERVIEWS...")
    
    try:
        # 1. Check current database
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"Database: {version}")
            
            # 2. Add UUID column if missing
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'jobapp_interview' AND column_name = 'uuid';
            """)
            
            if not cursor.fetchone():
                print("Adding UUID column...")
                cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN uuid UUID DEFAULT gen_random_uuid();")
                cursor.execute("UPDATE jobapp_interview SET uuid = gen_random_uuid() WHERE uuid IS NULL;")
                cursor.execute("ALTER TABLE jobapp_interview ADD CONSTRAINT jobapp_interview_uuid_unique UNIQUE (uuid);")
                print("✅ UUID column added")
            else:
                print("✅ UUID column exists")
        
        # 3. Run migrations
        print("Running migrations...")
        call_command('migrate', verbosity=0)
        
        # 4. Collect static files
        print("Collecting static files...")
        call_command('collectstatic', '--noinput', verbosity=0)
        
        print("🎉 ALL FIXES COMPLETED!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    fix_everything()