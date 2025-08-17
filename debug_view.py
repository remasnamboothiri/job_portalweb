#!/usr/bin/env python3
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.shortcuts import render
from django.contrib.auth import get_user_model
from jobapp.models import Interview, Application

User = get_user_model()

def debug_dashboard_view(request):
    user = User.objects.get(username='testcandidate')
    applications = Application.objects.filter(applicant=user)
    scheduled_interviews = Interview.objects.filter(candidate=user)
    
    return render(request, 'jobapp/debug_dashboard.html', {
        'user': user,
        'applications': applications,
        'scheduled_interviews': scheduled_interviews
    })

# Add this to urls.py temporarily
print("Add this to jobapp/urls.py:")
print("path('debug-dashboard/', views.debug_dashboard_view, name='debug_dashboard'),")
print("\nThen visit: http://localhost:8000/debug-dashboard/")