#!/usr/bin/env python3
"""
Debug script to check dashboard interview data
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from jobapp.models import Job, Interview, Application

User = get_user_model()

def debug_dashboard():
    print("=== DASHBOARD DEBUG ===")
    
    # Check users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    for user in users:
        print(f"  - {user.username} (recruiter: {user.is_recruiter})")
    
    # Check jobs
    jobs = Job.objects.all()
    print(f"\nTotal jobs: {jobs.count()}")
    for job in jobs:
        print(f"  - {job.title} by {job.posted_by.username}")
    
    # Check applications
    applications = Application.objects.all()
    print(f"\nTotal applications: {applications.count()}")
    for app in applications:
        print(f"  - {app.applicant.username} applied to {app.job.title}")
    
    # Check interviews
    interviews = Interview.objects.all()
    print(f"\nTotal interviews: {interviews.count()}")
    for interview in interviews:
        print(f"  - Interview for {interview.candidate_name} ({interview.candidate_email})")
        print(f"    Job: {interview.job_position.title}")
        print(f"    UUID: {interview.get_uuid}")
        print(f"    Date: {interview.interview_date}")
        print(f"    Candidate User: {interview.candidate}")
        print()
    
    # Test specific user dashboard
    if users.exists():
        test_user = users.filter(is_recruiter=False).first()
        if test_user:
            print(f"=== TESTING DASHBOARD FOR {test_user.username} ===")
            
            # Test applications query
            user_applications = Application.objects.filter(applicant=test_user)
            print(f"Applications for {test_user.username}: {user_applications.count()}")
            
            # Test interview queries
            print("\nTesting interview queries...")
            
            # Query 1: Direct candidate match
            try:
                interviews1 = Interview.objects.filter(candidate=test_user)
                print(f"Query 1 (candidate=user): {interviews1.count()} interviews")
                for i in interviews1:
                    print(f"  - {i.job_position.title}")
            except Exception as e:
                print(f"Query 1 failed: {e}")
            
            # Query 2: Email match
            try:
                interviews2 = Interview.objects.filter(candidate_email=test_user.email)
                print(f"Query 2 (email match): {interviews2.count()} interviews")
                for i in interviews2:
                    print(f"  - {i.job_position.title}")
            except Exception as e:
                print(f"Query 2 failed: {e}")
            
            # Query 3: Name match
            try:
                user_name = test_user.get_full_name() or test_user.username
                interviews3 = Interview.objects.filter(candidate_name__icontains=user_name)
                print(f"Query 3 (name match '{user_name}'): {interviews3.count()} interviews")
                for i in interviews3:
                    print(f"  - {i.job_position.title}")
            except Exception as e:
                print(f"Query 3 failed: {e}")

if __name__ == '__main__':
    debug_dashboard()