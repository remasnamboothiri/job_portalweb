#!/usr/bin/env python
"""
Test the complete interview flow
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

def test_interview_flow():
    print("Testing complete interview flow...")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model
        from jobapp.views import jobseeker_dashboard, interview_ready, start_interview_by_uuid
        from jobapp.models import Interview, Job
        
        User = get_user_model()
        factory = RequestFactory()
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='testcandidate',
            defaults={'email': 'candidate@example.com'}
        )
        
        # Create test job
        recruiter, created = User.objects.get_or_create(
            username='testrecruiter',
            defaults={'email': 'recruiter@example.com', 'is_recruiter': True}
        )
        
        job, created = Job.objects.get_or_create(
            title='Test Developer',
            defaults={
                'company': 'Test Company',
                'location': 'Remote',
                'description': 'Test job description',
                'posted_by': recruiter
            }
        )
        
        # Create test interview
        interview, created = Interview.objects.get_or_create(
            job_position=job,
            candidate=user,
            defaults={
                'candidate_name': user.username,
                'candidate_email': user.email,
                'interview_id': 'test-123-456'
            }
        )
        
        print(f"✅ Test data created - Interview ID: {interview.interview_id}")
        print(f"✅ Interview UUID: {interview.get_uuid}")
        
        # Test 1: Dashboard view
        request = factory.get('/dashboard/seeker/')
        request.user = user
        response = jobseeker_dashboard(request)
        
        if response.status_code == 200:
            print("✅ Dashboard view works")
        else:
            print(f"❌ Dashboard view failed: {response.status_code}")
        
        # Test 2: Interview ready view
        request = factory.get(f'/interview/ready/{interview.get_uuid}/')
        request.user = user
        response = interview_ready(request, interview.get_uuid)
        
        if response.status_code == 200:
            print("✅ Interview ready view works")
        else:
            print(f"❌ Interview ready view failed: {response.status_code}")
        
        # Test 3: Start interview view
        request = factory.get(f'/interview/start/{interview.get_uuid}/')
        request.user = user
        response = start_interview_by_uuid(request, interview.get_uuid)
        
        if response.status_code == 200:
            print("✅ Start interview view works")
        else:
            print(f"❌ Start interview view failed: {response.status_code}")
        
        print("\n🎉 Interview flow test completed successfully!")
        print(f"📋 Test interview link: /interview/ready/{interview.get_uuid}/")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_interview_flow()