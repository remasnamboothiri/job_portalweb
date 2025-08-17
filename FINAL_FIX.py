#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def final_fix():
    print("🔧 FINAL DATABASE FIX...")
    
    try:
        with connection.cursor() as cursor:
            # Check current table structure
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'jobapp_interview'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("Current columns:", [col[0] for col in columns])
            
            # Add missing columns
            missing_columns = []
            
            # Check for candidate_id
            if not any('candidate_id' in col[0] for col in columns):
                cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN candidate_id INTEGER REFERENCES jobapp_customuser(id);")
                missing_columns.append('candidate_id')
            
            # Check for uuid
            if not any('uuid' in col[0] for col in columns):
                cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN uuid UUID DEFAULT gen_random_uuid();")
                cursor.execute("UPDATE jobapp_interview SET uuid = gen_random_uuid() WHERE uuid IS NULL;")
                missing_columns.append('uuid')
            
            if missing_columns:
                print(f"✅ Added columns: {missing_columns}")
            else:
                print("✅ All columns exist")
        
        # Run migrations
        call_command('migrate', verbosity=0)
        print("✅ Migrations completed")
        
        print("🎉 FINAL FIX COMPLETED!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    final_fix()