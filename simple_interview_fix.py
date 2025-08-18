#!/usr/bin/env python
"""
Simple Interview Database Fix
Fixes the interview database schema issues
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
from django.conf import settings
import uuid

User = get_user_model()

def fix_interview_database():
    """Fix interview database issues"""
    print("Starting Interview Database Fix...")
    
    try:
        with connection.cursor() as cursor:
            # Check database type
            engine = settings.DATABASES['default']['ENGINE']
            is_postgresql = 'postgresql' in engine
            is_sqlite = 'sqlite' in engine
            
            print(f"Database type: {'PostgreSQL' if is_postgresql else 'SQLite' if is_sqlite else 'Unknown'}")
            
            if is_sqlite:
                # SQLite fix
                cursor.execute("PRAGMA table_info(jobapp_interview);")
                columns = {row[1]: row[2] for row in cursor.fetchall()}
                print(f"Current columns: {list(columns.keys())}")
                
                # Add missing columns
                if 'uuid' not in columns:
                    cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN uuid varchar(36) DEFAULT '';")
                    print("Added uuid column")
                
                if 'candidate_id' not in columns:
                    cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN candidate_id bigint;")
                    print("Added candidate_id column")
                
                if 'job_position_id' not in columns:
                    cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN job_position_id bigint;")
                    print("Added job_position_id column")
                
                # Fix UUID values
                cursor.execute("SELECT id FROM jobapp_interview WHERE uuid IS NULL OR uuid = '';")
                records = cursor.fetchall()
                
                for record in records:
                    new_uuid = str(uuid.uuid4())
                    cursor.execute("UPDATE jobapp_interview SET uuid = ? WHERE id = ?", [new_uuid, record[0]])
                
                print(f"Fixed {len(records)} UUID records")
                
                # Fix foreign keys
                cursor.execute("UPDATE jobapp_interview SET job_position_id = job_id WHERE job_position_id IS NULL AND job_id IS NOT NULL;")
                
            elif is_postgresql:
                # PostgreSQL fix
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'jobapp_interview';
                """)
                columns = [row[0] for row in cursor.fetchall()]
                print(f"Current columns: {columns}")
                
                # Add missing columns
                if 'uuid' not in columns:
                    cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN uuid uuid DEFAULT gen_random_uuid();")
                    print("Added uuid column")
                
                if 'candidate_id' not in columns:
                    cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN candidate_id bigint;")
                    print("Added candidate_id column")
                
                if 'job_position_id' not in columns:
                    cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN job_position_id bigint;")
                    print("Added job_position_id column")
                
                # Fix UUID values
                cursor.execute("UPDATE jobapp_interview SET uuid = gen_random_uuid() WHERE uuid IS NULL;")
                
                # Fix foreign keys
                cursor.execute("UPDATE jobapp_interview SET job_position_id = job_id WHERE job_position_id IS NULL AND job_id IS NOT NULL;")
            
            print("Database schema fixed successfully!")
            
            # Test the fix
            candidate = User.objects.filter(is_recruiter=False).first()
            if candidate:
                interviews = Interview.objects.filter(candidate=candidate)
                print(f"Test query successful: Found {interviews.count()} interviews for {candidate.username}")
            
            return True
            
    except Exception as e:
        print(f"Fix failed: {e}")
        return False

def create_sample_interview():
    """Create a sample interview for testing"""
    print("Creating sample interview...")
    
    try:
        candidate = User.objects.filter(is_recruiter=False).first()
        job = Job.objects.first()
        
        if not candidate or not job:
            print("No candidate or job found for sample interview")
            return False
        
        # Check if interview already exists
        existing = Interview.objects.filter(candidate=candidate, job_position=job).first()
        if existing:
            print(f"Sample interview already exists: {existing.uuid}")
            return True
        
        # Create new interview
        interview = Interview.objects.create(
            job_position=job,
            candidate=candidate,
            candidate_name=candidate.get_full_name() or candidate.username,
            candidate_email=candidate.email or f"{candidate.username}@example.com"
        )
        
        print(f"Sample interview created: {interview.uuid}")
        print(f"Candidate: {interview.candidate_name}")
        print(f"Job: {interview.job_position.title}")
        
        return True
        
    except Exception as e:
        print(f"Failed to create sample interview: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("INTERVIEW SYSTEM FIX")
    print("=" * 50)
    
    # Fix database
    if fix_interview_database():
        print("Database fix completed successfully!")
        
        # Create sample interview
        if create_sample_interview():
            print("Sample interview created!")
        
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Login as a candidate to see interview links")
        print("3. Click 'Start Interview' to test functionality")
        
    else:
        print("Database fix failed!")
        sys.exit(1)