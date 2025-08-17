#!/usr/bin/env python
"""
Fix for the interview database column issue
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.db import connection
from jobapp.models import Interview
import logging

logger = logging.getLogger(__name__)

def fix_interview_database():
    """Fix the interview database schema issue"""
    try:
        # Check current table structure
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'jobapp_interview'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("Current Interview table columns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
            
            # Check if candidate_id exists
            column_names = [col[0] for col in columns]
            
            if 'candidate_id' not in column_names and 'candidate' not in column_names:
                print("\n❌ Neither candidate nor candidate_id column found!")
                print("This suggests the Interview table needs to be recreated.")
                
                # Drop and recreate the table
                print("\n🔄 Recreating Interview table...")
                cursor.execute("DROP TABLE IF EXISTS jobapp_interview CASCADE;")
                
                # Create the table with correct schema
                cursor.execute("""
                    CREATE TABLE jobapp_interview (
                        id SERIAL PRIMARY KEY,
                        uuid UUID NOT NULL UNIQUE,
                        job_position_id INTEGER REFERENCES jobapp_job(id) ON DELETE CASCADE,
                        candidate_id INTEGER REFERENCES jobapp_customuser(id) ON DELETE CASCADE,
                        candidate_name VARCHAR(255) DEFAULT 'Unknown Candidate',
                        candidate_email VARCHAR(254) DEFAULT 'unknown@example.com',
                        interview_id VARCHAR(11) UNIQUE,
                        interview_link VARCHAR(500),
                        interview_date TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                
                print("✅ Interview table recreated successfully!")
                
            elif 'candidate' in column_names and 'candidate_id' not in column_names:
                print("\n❌ Found 'candidate' column but missing 'candidate_id'")
                print("This suggests a foreign key naming issue.")
                
                # Check the actual foreign key column name
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'jobapp_interview' 
                    AND column_name LIKE '%candidate%';
                """)
                candidate_columns = cursor.fetchall()
                print(f"Candidate-related columns: {candidate_columns}")
                
            else:
                print(f"\n✅ Found candidate column: {column_names}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error fixing interview database: {e}")
        return False

def test_interview_query():
    """Test the interview query that's failing"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get a test user
        user = User.objects.filter(id=2).first()
        if not user:
            print("❌ User with ID 2 not found")
            return False
            
        print(f"Testing interview query for user: {user.username}")
        
        # Try the query that's failing
        interviews = Interview.objects.filter(candidate=user)
        print(f"✅ Query successful! Found {interviews.count()} interviews")
        
        # Also test the alternative query
        interviews_alt = Interview.objects.filter(candidate_id=user.id)
        print(f"✅ Alternative query successful! Found {interviews_alt.count()} interviews")
        
        return True
        
    except Exception as e:
        print(f"❌ Interview query test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Starting Interview Database Fix...")
    
    # Fix database schema
    if fix_interview_database():
        print("\n🧪 Testing interview queries...")
        test_interview_query()
    
    print("\n✅ Fix completed!")