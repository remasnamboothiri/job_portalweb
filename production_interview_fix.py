#!/usr/bin/env python
"""
Production Interview Database Fix
Handles both SQLite (local) and PostgreSQL (production) databases
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

def get_database_type():
    """Detect database type"""
    engine = settings.DATABASES['default']['ENGINE']
    if 'postgresql' in engine:
        return 'postgresql'
    elif 'sqlite' in engine:
        return 'sqlite'
    else:
        return 'unknown'

def fix_postgresql_interview_table():
    """Fix PostgreSQL interview table"""
    print("🐘 Fixing PostgreSQL interview table...")
    
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'jobapp_interview'
            );
        """)
        
        if not cursor.fetchone()[0]:
            print("❌ Interview table doesn't exist. Running migrations...")
            os.system('python manage.py makemigrations')
            os.system('python manage.py migrate')
            return
        
        # Get current columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'jobapp_interview';
        """)
        
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        print(f"📋 Current columns: {list(columns.keys())}")
        
        # Add missing columns
        required_columns = {
            'uuid': 'uuid DEFAULT gen_random_uuid()',
            'candidate_id': 'bigint',
            'candidate_name': 'varchar(255) DEFAULT \'Unknown\'',
            'candidate_email': 'varchar(254) DEFAULT \'unknown@example.com\'',
            'job_position_id': 'bigint',
            'interview_date': 'timestamp with time zone',
            'created_at': 'timestamp with time zone DEFAULT NOW()'
        }
        
        for col_name, col_definition in required_columns.items():
            if col_name not in columns:
                print(f"➕ Adding column: {col_name}")
                try:
                    cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_definition};")
                    print(f"✅ Added: {col_name}")
                except Exception as e:
                    print(f"⚠️  Column {col_name} error: {e}")
        
        # Fix UUID column if it's empty
        cursor.execute("UPDATE jobapp_interview SET uuid = gen_random_uuid() WHERE uuid IS NULL;")
        
        # Fix foreign key relationships
        cursor.execute("""
            UPDATE jobapp_interview 
            SET job_position_id = job_id 
            WHERE job_position_id IS NULL AND job_id IS NOT NULL;
        """)
        
        print("✅ PostgreSQL table fixed!")

def fix_sqlite_interview_table():
    """Fix SQLite interview table"""
    print("📱 Fixing SQLite interview table...")
    
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='jobapp_interview';
        """)
        
        if not cursor.fetchone():
            print("❌ Interview table doesn't exist. Running migrations...")
            os.system('python manage.py makemigrations')
            os.system('python manage.py migrate')
            return
        
        # Get current columns
        cursor.execute("PRAGMA table_info(jobapp_interview);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        print(f"📋 Current columns: {list(columns.keys())}")
        
        # Add missing columns
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
                print(f"➕ Adding column: {col_name}")
                try:
                    if col_name == 'uuid':
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type} DEFAULT '';")
                    elif col_name == 'candidate_name':
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type} DEFAULT 'Unknown';")
                    elif col_name == 'candidate_email':
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type} DEFAULT 'unknown@example.com';")
                    else:
                        cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {col_name} {col_type};")
                    print(f"✅ Added: {col_name}")
                except Exception as e:
                    print(f"⚠️  Column {col_name} error: {e}")
        
        # Fix UUID values
        cursor.execute("SELECT id FROM jobapp_interview WHERE uuid IS NULL OR uuid = '';")
        records = cursor.fetchall()
        
        for record in records:
            new_uuid = str(uuid.uuid4())
            cursor.execute("UPDATE jobapp_interview SET uuid = ? WHERE id = ?", [new_uuid, record[0]])
        
        # Fix foreign key relationships
        cursor.execute("""
            UPDATE jobapp_interview 
            SET job_position_id = job_id 
            WHERE job_position_id IS NULL AND job_id IS NOT NULL;
        """)
        
        print("✅ SQLite table fixed!")

def test_interview_functionality():
    """Test if interview functionality works"""
    print("🧪 Testing interview functionality...")
    
    try:
        # Get test data
        candidate = User.objects.filter(is_recruiter=False).first()
        job = Job.objects.first()
        
        if not candidate or not job:
            print("⚠️  No test data available (need at least 1 candidate and 1 job)")
            return False
        
        # Try to query interviews (this was failing before)
        interviews = Interview.objects.filter(candidate=candidate)
        print(f"✅ Query successful: Found {interviews.count()} interviews for {candidate.username}")
        
        # Try to create a test interview
        test_interview = Interview.objects.create(
            job_position=job,
            candidate=candidate,
            candidate_name=candidate.get_full_name() or candidate.username,
            candidate_email=candidate.email or f"{candidate.username}@example.com"
        )
        
        print(f"✅ Interview creation successful: {test_interview.uuid}")
        
        # Test the dashboard query
        dashboard_interviews = Interview.objects.filter(
            candidate=candidate
        ).select_related('job_position').order_by('-created_at')
        
        print(f"✅ Dashboard query successful: {dashboard_interviews.count()} interviews")
        
        # Clean up test interview
        test_interview.delete()
        print("🧹 Test interview cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("🚀 Starting Production Interview Fix...")
    
    db_type = get_database_type()
    print(f"🔍 Detected database: {db_type}")
    
    try:
        with transaction.atomic():
            if db_type == 'postgresql':
                fix_postgresql_interview_table()
            elif db_type == 'sqlite':
                fix_sqlite_interview_table()
            else:
                print(f"❌ Unsupported database type: {db_type}")
                return False
            
            # Test the fix
            if test_interview_functionality():
                print("🎉 Interview system is now working correctly!")
                return True
            else:
                print("❌ Interview system still has issues")
                return False
                
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ INTERVIEW SYSTEM FIXED!")
    print("="*50)
    print("👉 Next steps:")
    print("1. Restart your application")
    print("2. Login as a recruiter and schedule an interview")
    print("3. Login as a candidate to see interview links on dashboard")
    print("4. Click 'Start Interview' to test the AI interview")
    print("="*50)