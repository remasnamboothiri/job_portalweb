#!/usr/bin/env python
"""
Check database status and configuration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.db import connection
from django.conf import settings

def main():
    print("[INFO] Checking database configuration...")
    
    # Check database settings
    db_config = settings.DATABASES['default']
    print(f"Database Engine: {db_config['ENGINE']}")
    
    if 'postgresql' in db_config['ENGINE']:
        print("[OK] Using PostgreSQL")
        print(f"Database Name: {db_config.get('NAME', 'Not specified')}")
        print(f"Host: {db_config.get('HOST', 'Not specified')}")
    else:
        print("[WARN] Using SQLite (development mode)")
    
    # Test connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("[OK] Database connection successful")
            
            # Check if Interview table exists
            if 'postgresql' in db_config['ENGINE']:
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_name = 'jobapp_interview';
                """)
            else:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='jobapp_interview';
                """)
            
            table_exists = cursor.fetchone()
            if table_exists:
                print("[OK] Interview table exists")
                
                # Check UUID column
                if 'postgresql' in db_config['ENGINE']:
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name='jobapp_interview' AND column_name='uuid';
                    """)
                else:
                    cursor.execute("PRAGMA table_info(jobapp_interview);")
                    columns = [row[1] for row in cursor.fetchall()]
                    uuid_exists = 'uuid' in columns
                    
                if 'postgresql' in db_config['ENGINE']:
                    uuid_exists = cursor.fetchone()
                
                if uuid_exists:
                    print("[OK] UUID column exists")
                    
                    # Count records
                    cursor.execute("SELECT COUNT(*) FROM jobapp_interview;")
                    count = cursor.fetchone()[0]
                    print(f"[INFO] Interview records: {count}")
                else:
                    print("[ERROR] UUID column missing - needs migration")
            else:
                print("[ERROR] Interview table missing - needs migration")
                
    except Exception as e:
        print(f"[ERROR] Database error: {e}")

if __name__ == '__main__':
    main()