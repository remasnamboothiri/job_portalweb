#!/usr/bin/env python3
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from jobapp.models import Interview

User = get_user_model()

def test_template():
    print("=== TEMPLATE TEST ===")
    
    user = User.objects.get(username='testcandidate')
    interviews = Interview.objects.filter(candidate=user)
    
    print(f"User: {user.username}")
    print(f"Interviews: {interviews.count()}")
    
    context = {
        'user': user,
        'applications': [],
        'scheduled_interviews': list(interviews),
        'request': type('MockRequest', (), {
            'scheme': 'http',
            'get_host': lambda: 'localhost:8000'
        })()
    }
    
    try:
        html = render_to_string('jobapp/jobseeker_dashboard.html', context)
        
        # Check if interview content is in HTML
        if 'Your Scheduled Interviews' in html:
            print("✅ Interview section found in HTML")
        else:
            print("❌ Interview section NOT found")
            
        if 'interview-link-' in html:
            print("✅ Interview links found in HTML")
        else:
            print("❌ Interview links NOT found")
            
        if 'Start Interview' in html:
            print("✅ Start Interview button found")
        else:
            print("❌ Start Interview button NOT found")
            
        # Count interview occurrences
        interview_count = html.count('Frontend Developer') + html.count('Test Developer')
        print(f"Interview job titles found: {interview_count}")
        
    except Exception as e:
        print(f"Template error: {e}")

if __name__ == '__main__':
    test_template()