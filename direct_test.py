#!/usr/bin/env python3
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from jobapp.models import Interview, Application
from jobapp.views import jobseeker_dashboard
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

User = get_user_model()

def test_dashboard_data():
    print("=== DIRECT DASHBOARD TEST ===")
    
    # Get user
    user = User.objects.get(username='testcandidate')
    print(f"User: {user.username}")
    
    # Check applications
    applications = Application.objects.filter(applicant=user)
    print(f"Applications: {applications.count()}")
    
    # Check interviews - exact same query as view
    scheduled_interviews = []
    try:
        scheduled_interviews = list(Interview.objects.filter(
            candidate=user
        ).select_related('job_position').order_by('-created_at'))
        print(f"Interviews found: {len(scheduled_interviews)}")
        
        for interview in scheduled_interviews:
            print(f"  - {interview.job_position.title}")
            print(f"    UUID: {interview.get_uuid}")
            print(f"    Candidate: {interview.candidate}")
            print(f"    Email: {interview.candidate_email}")
    except Exception as e:
        print(f"Interview query error: {e}")
    
    # Test view directly
    factory = RequestFactory()
    request = factory.get('/dashboard/jobseeker/')
    request.user = user
    
    # Add session
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    try:
        from django.template.response import TemplateResponse
        response = jobseeker_dashboard(request)
        
        if isinstance(response, TemplateResponse):
            context = response.context_data
            print(f"\nView context:")
            print(f"  applications: {len(context.get('applications', []))}")
            print(f"  scheduled_interviews: {len(context.get('scheduled_interviews', []))}")
            
            # Check if interviews are in context
            interviews_in_context = context.get('scheduled_interviews', [])
            if interviews_in_context:
                print("✅ Interviews ARE in context!")
                for i in interviews_in_context:
                    print(f"    - {i.job_position.title} (UUID: {i.get_uuid})")
            else:
                print("❌ NO interviews in context")
        
    except Exception as e:
        print(f"View test error: {e}")

if __name__ == '__main__':
    test_dashboard_data()