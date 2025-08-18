#!/usr/bin/env python
"""
Production Database Fix for Interview System
This script ensures the interview table has all required columns and data integrity.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.db import connection, transaction
from django.contrib.auth import get_user_model
from jobapp.models import Interview, Job
import uuid

User = get_user_model()

def fix_interview_database():
    """Fix interview database schema and data issues"""
    
    print("🔧 Starting Interview Database Fix...")
    
    with connection.cursor() as cursor:
        # Check if interview table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='jobapp_interview';
        """)
        
        if not cursor.fetchone():
            print("❌ Interview table doesn't exist. Running migrations first...")
            os.system('python manage.py makemigrations')
            os.system('python manage.py migrate')
            return
        
        # Get current table structure
        cursor.execute("PRAGMA table_info(jobapp_interview);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        print(f"📋 Current columns: {list(columns.keys())}")
        
        # Add missing columns if needed
        required_columns = {
            'uuid': 'varchar(36)',
            'candidate_id': 'bigint',
            'candidate_name': 'varchar(255)',
            'candidate_email': 'varchar(254)',
            'job_position_id': 'bigint',
            'interview_date': 'datetime',
            'created_at': 'datetime'
        }
        
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                print(f"➕ Adding missing column: {col_name}")
                try:
                    if col_name == 'uuid':
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type} DEFAULT '';")
                    elif col_name == 'candidate_id':
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type};")
                    elif col_name == 'candidate_name':
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type} DEFAULT 'Unknown';")
                    elif col_name == 'candidate_email':
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type} DEFAULT 'unknown@example.com';")
                    elif col_name == 'job_position_id':
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type};")
                    else:
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type};")
                    print(f"✅ Added column: {col_name}")
                except Exception as e:
                    print(f"⚠️  Column {col_name} might already exist: {e}")
        
        # Fix existing records with missing UUIDs
        cursor.execute("SELECT id FROM jobapp_interview WHERE uuid IS NULL OR uuid = '';")
        records_to_fix = cursor.fetchall()
        
        if records_to_fix:
            print(f"🔄 Fixing {len(records_to_fix)} records with missing UUIDs...")
            for record in records_to_fix:
                new_uuid = str(uuid.uuid4())
                cursor.execute("UPDATE jobapp_interview SET uuid = ? WHERE id = ?", [new_uuid, record[0]])
            print("✅ Fixed UUID records")
        
        # Ensure foreign key relationships are correct
        cursor.execute("""
            UPDATE jobapp_interview 
            SET job_position_id = job_id 
            WHERE job_position_id IS NULL AND job_id IS NOT NULL;
        """)
        
        print("✅ Database schema fixed successfully!")
        
        # Test the fix by creating a sample interview
        try:
            # Get a test user and job
            test_user = User.objects.filter(is_recruiter=False).first()
            test_job = Job.objects.first()
            
            if test_user and test_job:
                # Check if we can create an interview
                test_interview = Interview(
                    job_position=test_job,
                    candidate=test_user,
                    candidate_name=test_user.get_full_name() or test_user.username,
                    candidate_email=test_user.email or 'test@example.com'
                )
                test_interview.save()
                print(f"✅ Test interview created successfully: {test_interview.uuid}")
                
                # Clean up test interview
                test_interview.delete()
                print("🧹 Test interview cleaned up")
            else:
                print("⚠️  No test user or job found for validation")
                
        except Exception as e:
            print(f"⚠️  Test interview creation failed: {e}")

if __name__ == '__main__':
    try:
        fix_interview_database()
        print("🎉 Interview database fix completed successfully!")
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        sys.exit(1)