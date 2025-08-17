#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.db import connection, transaction
from django.core.management import call_command

def emergency_fix():
    print("🚨 EMERGENCY FIX STARTING...")
    
    try:
        # 1. Add UUID column directly to PostgreSQL
        print("1. Adding UUID column to PostgreSQL...")
        with connection.cursor() as cursor:
            # Check if column exists
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'jobapp_interview' AND column_name = 'uuid';
            """)
            
            if not cursor.fetchone():
                print("   Adding UUID column...")
                cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN uuid UUID;")
                
                # Generate UUIDs for existing records
                cursor.execute("""
                    UPDATE jobapp_interview 
                    SET uuid = gen_random_uuid() 
                    WHERE uuid IS NULL;
                """)
                
                # Add unique constraint
                cursor.execute("ALTER TABLE jobapp_interview ADD CONSTRAINT jobapp_interview_uuid_unique UNIQUE (uuid);")
                print("   ✅ UUID column added successfully")
            else:
                print("   ✅ UUID column already exists")
        
        # 2. Run migrations
        print("2. Running migrations...")
        call_command('migrate', verbosity=0)
        print("   ✅ Migrations completed")
        
        # 3. Collect static files
        print("3. Collecting static files...")
        call_command('collectstatic', '--noinput', verbosity=0)
        print("   ✅ Static files collected")
        
        print("🎉 EMERGENCY FIX COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ EMERGENCY FIX FAILED: {e}")
        return False

if __name__ == '__main__':
    success = emergency_fix()
    sys.exit(0 if success else 1)