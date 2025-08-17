import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from jobapp.models import Interview, Job, Application

User = get_user_model()

# Check user vismaya
try:
    user = User.objects.get(username='vismaya')
    print(f"User: {user.username} (ID: {user.id})")
    
    # Check applications
    applications = Application.objects.filter(user=user)
    print(f"Applications: {applications.count()}")
    
    # Check interviews - try both ways
    try:
        interviews = Interview.objects.filter(candidate=user)
        print(f"Interviews (candidate field): {interviews.count()}")
        for interview in interviews:
            print(f"  - Interview {interview.id}: {interview.job_position.title if interview.job_position else 'No job'}")
    except Exception as e:
        print(f"Error with candidate field: {e}")
    
    try:
        # Alternative query through applications
        interview_apps = Application.objects.filter(user=user, interview__isnull=False)
        print(f"Applications with interviews: {interview_apps.count()}")
        for app in interview_apps:
            print(f"  - App {app.id} -> Interview {app.interview.id}: {app.job.title}")
    except Exception as e:
        print(f"Error with application interviews: {e}")
        
except User.DoesNotExist:
    print("User vismaya not found")

# Check all interviews in database
print(f"\nTotal interviews in database: {Interview.objects.count()}")
for interview in Interview.objects.all():
    print(f"Interview {interview.id}: Job={interview.job_position.title if interview.job_position else 'None'}, Candidate={getattr(interview, 'candidate', 'No candidate field')}")