from django.core.management.base import BaseCommand
from django.db import connection
from jobapp.models import Interview
import uuid

class Command(BaseCommand):
    help = 'Fix Interview model schema issues'

    def handle(self, *args, **options):
        self.stdout.write('Checking Interview model schema...')
        
        try:
            # Test if we can query interviews without uuid field
            interviews = Interview.objects.all()[:1]
            for interview in interviews:
                # Try to access uuid field
                try:
                    uuid_val = interview.uuid
                    self.stdout.write(f'UUID field accessible: {uuid_val}')
                except Exception as e:
                    self.stdout.write(f'UUID field issue: {e}')
                    
                # Ensure interview_id exists
                if not interview.interview_id:
                    interview.interview_id = interview.generate_unique_id()
                    interview.save()
                    self.stdout.write(f'Fixed interview_id for interview {interview.id}')
                    
            self.stdout.write(self.style.SUCCESS('Interview schema check completed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking schema: {e}'))
            
        # Try to run migrations
        try:
            from django.core.management import call_command
            self.stdout.write('Running migrations...')
            call_command('migrate', verbosity=1)
            self.stdout.write(self.style.SUCCESS('Migrations completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration error: {e}'))