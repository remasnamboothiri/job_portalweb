#!/usr/bin/env python
"""
Test the jobseeker dashboard view
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

def test_dashboard():
    print("Testing jobseeker dashboard...")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model
        from jobapp.views import jobseeker_dashboard
        from jobapp.models import Interview, Application
        
        User = get_user_model()
        factory = RequestFactory()
        
        # Create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        # Create a mock request
        request = factory.get('/dashboard/seeker/')
        request.user = user
        
        # Test the view
        response = jobseeker_dashboard(request)
        
        if response.status_code == 200:
            print("SUCCESS: Dashboard view works correctly")
            print(f"Response status: {response.status_code}")
        else:
            print(f"ERROR: Dashboard returned status {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Dashboard test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_dashboard()