#!/usr/bin/env python
"""
Simple test for interview flow
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

def test_interview_flow():
    print("Testing interview flow...")
    
    try:
        from jobapp.models import Interview, Job
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Test Interview model
        count = Interview.objects.count()
        print(f"SUCCESS: Interview model accessible, found {count} records")
        
        # Test creating interview
        if Job.objects.exists() and User.objects.exists():
            job = Job.objects.first()
            user = User.objects.first()
            
            interview, created = Interview.objects.get_or_create(
                job_position=job,
                candidate=user,
                defaults={
                    'candidate_name': user.username,
                    'candidate_email': user.email or 'test@example.com',
                    'interview_id': 'test-123'
                }
            )
            
            print(f"SUCCESS: Interview created/found - ID: {interview.interview_id}")
            print(f"SUCCESS: Interview UUID: {interview.get_uuid}")
            print(f"SUCCESS: Interview link: /interview/ready/{interview.get_uuid}/")
            
        print("SUCCESS: Interview flow test completed!")
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_interview_flow()