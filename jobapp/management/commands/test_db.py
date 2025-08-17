from django.core.management.base import BaseCommand
from jobapp.models import Interview, Job, CustomUser

class Command(BaseCommand):
    help = 'Test database operations'

    def handle(self, *args, **options):
        try:
            # Test Interview model
            interview_count = Interview.objects.count()
            self.stdout.write(f"Interview count: {interview_count}")
            
            # Test if UUID field works
            if interview_count > 0:
                first_interview = Interview.objects.first()
                self.stdout.write(f"First interview UUID: {first_interview.uuid}")
                self.stdout.write(f"First interview ID: {first_interview.id}")
            
            # Test Job model
            job_count = Job.objects.count()
            self.stdout.write(f"Job count: {job_count}")
            
            # Test User model
            user_count = CustomUser.objects.count()
            self.stdout.write(f"User count: {user_count}")
            
            self.stdout.write(self.style.SUCCESS('Database test completed successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Database test failed: {e}'))