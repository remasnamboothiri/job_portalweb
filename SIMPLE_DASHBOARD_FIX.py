#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.models import Interview, Application

def fix_dashboard():
    print("🔧 FIXING DASHBOARD WITHOUT UUID...")
    
    # Create a simple view that doesn't use UUID
    views_content = '''
@login_required
def jobseeker_dashboard(request):
    applications = Application.objects.filter(applicant=request.user)
    try:
        profile = Profile.objects.filter(user=request.user).first()
    except Exception:
        profile = None
    
    # Simple interview query without UUID
    scheduled_interviews = []
    try:
        from jobapp.models import Interview
        scheduled_interviews = Interview.objects.filter(
            candidate=request.user
        ).order_by('-created_at')[:10]
        
        logger.info(f"Dashboard for {request.user.username}: {len(applications)} applications, {len(scheduled_interviews)} interviews")
        
    except Exception as e:
        logger.warning(f"Could not fetch interviews: {e}")
        scheduled_interviews = []
    
    return render(request, 'jobapp/jobseeker_dashboard.html', {
        'applications': applications, 
        'profile': profile,
        'scheduled_interviews': scheduled_interviews
    })
'''
    
    print("✅ Dashboard fix ready")
    print("Replace the jobseeker_dashboard function in views.py with the code above")
    print("This removes UUID dependency from the dashboard")

if __name__ == '__main__':
    fix_dashboard()