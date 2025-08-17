import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("All users in database:")
for user in User.objects.all():
    print(f"  - {user.username} (ID: {user.id}, Email: {user.email})")