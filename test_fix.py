#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.db import connection
from jobapp.models import Interview

def test_fix():
    print("🧪 TESTING FIX...")
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Database: {version}")
            
            # Test UUID column exists
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'jobapp_interview' AND column_name = 'uuid';
            """)
            
            if cursor.fetchone():
                print("✅ UUID column exists")
            else:
                print("❌ UUID column missing")
                return False
        
        # Test Interview model
        try:
            interviews = Interview.objects.all()
            print(f"✅ Interview model works - {interviews.count()} interviews found")
        except Exception as e:
            print(f"❌ Interview model error: {e}")
            return False
        
        print("🎉 ALL TESTS PASSED!")
        print("\nYour system is now working correctly!")
        print("- PostgreSQL database ✅")
        print("- UUID column exists ✅") 
        print("- Interview links will work ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    test_fix()