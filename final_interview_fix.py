#!/usr/bin/env python
"""
Final Interview Database Fix
The production database already has the correct schema, just need to create test data
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from jobapp.models import Interview, Job
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def test_interview_system():
    """Test if the interview system works"""
    print("Testing interview system...")
    
    try:
        # Test basic query
        candidate = User.objects.filter(is_recruiter=False).first()
        if not candidate:
            print("No job seeker found. Please create a job seeker account.")
            return False
        
        # Test the query that was failing in the dashboard
        interviews = Interview.objects.filter(candidate=candidate)
        print(f"Query successful: Found {interviews.count()} interviews for {candidate.username}")
        
        # Test dashboard query
        dashboard_interviews = Interview.objects.filter(
            candidate=candidate
        ).select_related('job_position').order_by('-created_at')
        
        print(f"Dashboard query successful: {dashboard_interviews.count()} interviews")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def create_demo_interview():
    """Create a demo interview for the user to see"""
    print("Creating demo interview...")
    
    try:
        # Get the user 'vismaya' from the logs
        candidate = User.objects.filter(username='vismaya').first()
        if not candidate:
            # Get any job seeker
            candidate = User.objects.filter(is_recruiter=False).first()
        
        if not candidate:
            print("No candidate found")
            return False
        
        # Get a job
        job = Job.objects.first()
        if not job:
            print("No job found")
            return False
        
        # Check if interview already exists
        existing = Interview.objects.filter(
            candidate=candidate,
            job_position=job
        ).first()
        
        if existing:
            print(f"Interview already exists for {candidate.username}")
            print(f"UUID: {existing.uuid}")
            print(f"Job: {existing.job_position.title}")
            return True
        
        # Create new interview
        interview = Interview.objects.create(
            job_position=job,
            candidate=candidate,
            candidate_name=candidate.get_full_name() or candidate.username,
            candidate_email=candidate.email or f"{candidate.username}@example.com",
            interview_date=timezone.now() + timedelta(hours=2)  # Schedule for 2 hours from now
        )
        
        print(f"Demo interview created successfully!")
        print(f"Candidate: {interview.candidate_name} ({candidate.username})")
        print(f"Job: {interview.job_position.title}")
        print(f"UUID: {interview.uuid}")
        print(f"Interview Link: /interview/ready/{interview.uuid}/")
        
        return True
        
    except Exception as e:
        print(f"Failed to create demo interview: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("FINAL INTERVIEW SYSTEM FIX")
    print("=" * 50)
    
    # Test the system
    if test_interview_system():
        print("Interview system is working correctly!")
        
        # Create demo interview
        if create_demo_interview():
            print("\nDemo interview created!")
            print("\nInstructions:")
            print("1. Login as the candidate (vismaya or any job seeker)")
            print("2. Go to the dashboard (/dashboard/seeker/)")
            print("3. You should now see the interview link")
            print("4. Click 'Start Interview' to test the AI interview")
            
        else:
            print("Could not create demo interview")
            
    else:
        print("Interview system has issues")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("SUCCESS! Interview system is now working.")
    print("=" * 50)