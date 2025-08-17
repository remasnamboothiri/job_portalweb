#!/usr/bin/env python3
"""
Test the fixed dashboard functionality
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from jobapp.models import Interview

User = get_user_model()

def test_dashboard_fix():
    print("Testing Dashboard Fix...")
    
    # Get test user
    try:
        user = User.objects.get(username='testcandidate')
        print(f"Testing with user: {user.username}")
    except User.DoesNotExist:
        print("Test user 'testcandidate' not found. Please run create_test_interview.py first.")
        return
    
    # Check interviews for this user
    interviews = Interview.objects.filter(candidate=user)
    print(f"Found {interviews.count()} interviews for {user.username}")
    
    for interview in interviews:
        print(f"  - {interview.job_position.title}")
        print(f"    UUID: {interview.get_uuid}")
        print(f"    Date: {interview.interview_date}")
        print(f"    Link: /interview/ready/{interview.get_uuid}/")
    
    # Test the dashboard view
    client = Client()
    client.force_login(user)
    
    try:
        response = client.get('/dashboard/jobseeker/')
        print(f"\nDashboard response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check if interview links are in the response
            if 'interview-link-' in content:
                print("✅ Interview links found in dashboard!")
            else:
                print("❌ Interview links NOT found in dashboard")
            
            # Check if Start Interview button is present
            if 'Start Interview' in content:
                print("✅ Start Interview button found!")
            else:
                print("❌ Start Interview button NOT found")
            
            # Check if copy functionality is present
            if 'copyInterviewLink' in content:
                print("✅ Copy functionality found!")
            else:
                print("❌ Copy functionality NOT found")
                
        else:
            print(f"❌ Dashboard failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard test error: {e}")
    
    print("\n=== SOLUTION ===")
    print("1. Login as 'testcandidate' (password: testpass123)")
    print("2. Go to /dashboard/jobseeker/")
    print("3. You should see interview links with copy buttons")
    print("4. Click 'Start Interview' to go to interview ready page")
    print("5. Click 'Start AI Interview' to begin the interview")

if __name__ == '__main__':
    test_dashboard_fix()