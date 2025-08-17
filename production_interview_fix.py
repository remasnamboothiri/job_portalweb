#!/usr/bin/env python
"""
Production fix for interview database issues
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.db import connection, transaction
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

def fix_production_database():
    """Fix the production database issues"""
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                print("🔧 Fixing production database...")
                
                # Check if interview table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'jobapp_interview'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    print("📋 Creating interview table...")
                    cursor.execute("""
                        CREATE TABLE jobapp_interview (
                            id SERIAL PRIMARY KEY,
                            uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                            job_position_id INTEGER NOT NULL,
                            candidate_id INTEGER,
                            candidate_name VARCHAR(255) DEFAULT 'Unknown Candidate',
                            candidate_email VARCHAR(254) DEFAULT 'unknown@example.com',
                            interview_id VARCHAR(11) UNIQUE,
                            interview_link VARCHAR(500),
                            interview_date TIMESTAMP WITH TIME ZONE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            FOREIGN KEY (job_position_id) REFERENCES jobapp_job(id) ON DELETE CASCADE,
                            FOREIGN KEY (candidate_id) REFERENCES jobapp_customuser(id) ON DELETE SET NULL
                        );
                    """)
                    print("✅ Interview table created")
                else:
                    print("✅ Interview table already exists")
                    
                    # Check and fix columns if needed
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'jobapp_interview';
                    """)
                    columns = [row[0] for row in cursor.fetchall()]
                    
                    # Add missing columns
                    if 'uuid' not in columns:
                        cursor.execute("""
                            ALTER TABLE jobapp_interview 
                            ADD COLUMN uuid UUID UNIQUE DEFAULT gen_random_uuid();
                        """)
                        print("✅ Added uuid column")
                    
                    if 'candidate_id' not in columns:
                        cursor.execute("""
                            ALTER TABLE jobapp_interview 
                            ADD COLUMN candidate_id INTEGER REFERENCES jobapp_customuser(id) ON DELETE SET NULL;
                        """)
                        print("✅ Added candidate_id column")
                    
                    if 'created_at' not in columns:
                        cursor.execute("""
                            ALTER TABLE jobapp_interview 
                            ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                        """)
                        print("✅ Added created_at column")
                
                # Test the queries that were failing
                print("\n🧪 Testing interview queries...")
                
                # Test user query
                test_user = User.objects.first()
                if test_user:
                    cursor.execute("""
                        SELECT COUNT(*) FROM jobapp_interview 
                        WHERE candidate_id = %s;
                    """, [test_user.id])
                    count = cursor.fetchone()[0]
                    print(f"✅ User interview query works: {count} interviews found")
                
                # Test job query
                cursor.execute("""
                    SELECT COUNT(*) FROM jobapp_interview i
                    JOIN jobapp_job j ON i.job_position_id = j.id;
                """)
                count = cursor.fetchone()[0]
                print(f"✅ Job interview query works: {count} total interviews")
                
        print("✅ Production database fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Production fix failed: {e}")
        return False

def test_interview_functionality():
    """Test that interview functionality works"""
    try:
        from jobapp.models import Interview, Job
        
        print("\n🧪 Testing Interview model functionality...")
        
        # Test model import
        print("✅ Interview model imported successfully")
        
        # Test basic query
        interview_count = Interview.objects.count()
        print(f"✅ Interview count query works: {interview_count} interviews")
        
        # Test user filtering
        test_user = User.objects.first()
        if test_user:
            user_interviews = Interview.objects.filter(candidate=test_user).count()
            print(f"✅ User interview filtering works: {user_interviews} interviews for user")
        
        # Test job filtering
        test_job = Job.objects.first()
        if test_job:
            job_interviews = Interview.objects.filter(job_position=test_job).count()
            print(f"✅ Job interview filtering works: {job_interviews} interviews for job")
        
        print("✅ All interview functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Interview functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Production Interview Fix...")
    
    # Fix database
    if fix_production_database():
        # Test functionality
        test_interview_functionality()
    
    print("\n🎉 Production fix completed!")