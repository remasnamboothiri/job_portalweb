import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.models import Interview

# Update all interviews without UUIDs
interviews = Interview.objects.filter(uuid__isnull=True)
print(f"Found {interviews.count()} interviews without UUIDs")

for interview in interviews:
    interview.uuid = uuid.uuid4()
    interview.save()
    print(f"Updated interview {interview.id} with UUID {interview.uuid}")

print("All interviews now have UUIDs")