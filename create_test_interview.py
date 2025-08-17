#!/usr/bin/env python3
"""
Create a test interview with proper data
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from jobapp.models import Job, Interview
from django.utils import timezone

User = get_user_model()

def create_test_interview():
    print("Creating test interview with proper data...")
    
    # Get or create test users
    try:
        candidate = User.objects.get(username='testcandidate')
    except User.DoesNotExist:
        candidate = User.objects.create_user(
            username='testcandidate',
            email='candidate@test.com',
            password='testpass123',
            is_recruiter=False
        )
        print(f"Created candidate: {candidate.username}")
    
    try:
        recruiter = User.objects.get(username='testrecruiter')
    except User.DoesNotExist:
        recruiter = User.objects.create_user(
            username='testrecruiter',
            email='recruiter@test.com',
            password='testpass123',
            is_recruiter=True
        )
        print(f"Created recruiter: {recruiter.username}")
    
    # Get or create test job
    job, created = Job.objects.get_or_create(
        title='Frontend Developer',
        defaults={
            'company': 'Tech Solutions Inc',
            'location': 'Remote',
            'description': 'We are looking for a skilled Frontend Developer to join our team.',
            'posted_by': recruiter,
            'enable_ai_interview': True
        }
    )
    if created:
        print(f"Created job: {job.title}")
    
    # Create interview with proper date
    interview_date = timezone.now() + timedelta(days=1)  # Tomorrow
    
    interview, created = Interview.objects.get_or_create(
        job_position=job,
        candidate=candidate,
        defaults={
            'candidate_name': candidate.get_full_name() or candidate.username,
            'candidate_email': candidate.email,
            'interview_date': interview_date
        }
    )
    
    if created:
        print(f"Created interview: {interview.candidate_name} for {interview.job_position.title}")
    else:
        # Update existing interview with proper date
        interview.interview_date = interview_date
        interview.save()
        print(f"Updated interview: {interview.candidate_name} for {interview.job_position.title}")
    
    print(f"Interview details:")
    print(f"  - UUID: {interview.get_uuid}")
    print(f"  - Date: {interview.interview_date}")
    print(f"  - Candidate: {interview.candidate_name} ({interview.candidate_email})")
    print(f"  - Job: {interview.job_position.title}")
    print(f"  - Company: {interview.job_position.company}")
    
    # Test the interview link
    from django.urls import reverse
    try:
        interview_url = reverse('interview_ready', args=[interview.get_uuid])
        print(f"  - Interview Link: http://localhost:8000{interview_url}")
    except Exception as e:
        print(f"  - Link generation error: {e}")
    
    print("\nTest interview created successfully!")
    print("Now try logging in as 'testcandidate' (password: testpass123) to see the interview link in the dashboard.")

if __name__ == '__main__':
    create_test_interview()