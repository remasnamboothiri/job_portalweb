import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from jobapp.models import Interview, Application

User = get_user_model()

# Check testuser (ID 2)
user = User.objects.get(id=2)
print(f"User: {user.username} (ID: {user.id})")

# Check applications
applications = Application.objects.filter(user=user)
print(f"Applications: {applications.count()}")
for app in applications:
    print(f"  - App {app.id}: {app.job.title}")

# Check interviews
try:
    interviews = Interview.objects.filter(candidate=user)
    print(f"Interviews: {interviews.count()}")
    for interview in interviews:
        print(f"  - Interview {interview.id}: {interview.job_position.title}")
except Exception as e:
    print(f"Error getting interviews: {e}")

# Create a test interview for testuser
from jobapp.models import Job
import uuid

try:
    job = Job.objects.first()
    if job:
        interview = Interview.objects.create(
            job_position=job,
            candidate=user,
            uuid=uuid.uuid4(),
            interview_date='2025-01-20 10:00:00'
        )
        print(f"Created test interview {interview.id} for {user.username}")
    else:
        print("No jobs available to create interview")
except Exception as e:
    print(f"Error creating interview: {e}")