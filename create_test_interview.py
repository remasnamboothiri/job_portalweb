#!/usr/bin/env python
"""
Create Test Interview for Demonstration
This script creates a test interview to show the functionality working.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from jobapp.models import Interview, Job
from django.utils import timezone

User = get_user_model()

def create_test_interview():
    """Create a test interview for demonstration"""
    
    print("🎯 Creating test interview...")
    
    try:
        # Get a job seeker (candidate)
        candidate = User.objects.filter(is_recruiter=False).first()
        if not candidate:
            print("❌ No job seeker found. Please create a job seeker account first.")
            return False
        
        # Get a job
        job = Job.objects.first()
        if not job:
            print("❌ No jobs found. Please create a job first.")
            return False
        
        # Check if interview already exists
        existing = Interview.objects.filter(
            candidate=candidate,
            job_position=job
        ).first()
        
        if existing:
            print(f"✅ Interview already exists: {existing.uuid}")
            print(f"📧 Candidate: {existing.candidate_name} ({existing.candidate_email})")
            print(f"💼 Job: {existing.job_position.title}")
            print(f"🔗 Interview Link: /interview/ready/{existing.uuid}/")
            return True
        
        # Create new interview
        interview = Interview.objects.create(
            job_position=job,
            candidate=candidate,
            candidate_name=candidate.get_full_name() or candidate.username,
            candidate_email=candidate.email or f"{candidate.username}@example.com",
            interview_date=timezone.now() + timedelta(hours=1)  # Schedule for 1 hour from now
        )
        
        print("✅ Test interview created successfully!")
        print(f"📧 Candidate: {interview.candidate_name} ({interview.candidate_email})")
        print(f"💼 Job: {interview.job_position.title}")
        print(f"🆔 Interview UUID: {interview.uuid}")
        print(f"🔗 Interview Link: /interview/ready/{interview.uuid}/")
        print(f"📅 Scheduled: {interview.interview_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test interview: {e}")
        return False

if __name__ == '__main__':
    success = create_test_interview()
    if success:
        print("\n🎉 Test interview setup completed!")
        print("👉 Now login as the candidate and check the dashboard to see the interview link.")
    else:
        print("\n❌ Test interview setup failed!")
        sys.exit(1)