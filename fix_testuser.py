import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from jobapp.models import Interview, Application, Job
import uuid

User = get_user_model()

# Check testuser (ID 2) - this is the user logged in as "vismaya"
user = User.objects.get(id=2)
print(f"User: {user.username} (ID: {user.id})")

# Check applications using correct field name
applications = Application.objects.filter(applicant=user)
print(f"Applications: {applications.count()}")

# Create a test interview for testuser
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
        print(f"Interview UUID: {interview.uuid}")
        print(f"Interview link: http://localhost:8000/interview/{interview.uuid}/")
    else:
        print("No jobs available")
except Exception as e:
    print(f"Error creating interview: {e}")

# Now check interviews for this user
try:
    interviews = Interview.objects.filter(candidate=user)
    print(f"Total interviews for {user.username}: {interviews.count()}")
    for interview in interviews:
        print(f"  - Interview {interview.id}: {interview.job_position.title} (UUID: {interview.uuid})")
except Exception as e:
    print(f"Error getting interviews: {e}")