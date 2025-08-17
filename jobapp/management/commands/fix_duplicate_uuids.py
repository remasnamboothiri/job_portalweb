from django.core.management.base import BaseCommand
from django.db import connection
from jobapp.models import Interview
import uuid

class Command(BaseCommand):
    help = 'Fix duplicate UUIDs in Interview table'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # Check if UUID column exists first
                if 'postgresql' in connection.settings_dict['ENGINE']:
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name='jobapp_interview' AND column_name='uuid';
                    """)
                    uuid_exists = cursor.fetchone()
                else:
                    # SQLite
                    cursor.execute("PRAGMA table_info(jobapp_interview);")
                    columns = [row[1] for row in cursor.fetchall()]
                    uuid_exists = 'uuid' in columns
                
                if not uuid_exists:
                    self.stdout.write("UUID column doesn't exist - adding it...")
                    
                    if 'postgresql' in connection.settings_dict['ENGINE']:
                        cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN uuid UUID;")
                    else:
                        cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN uuid TEXT;")
                    
                    # Populate UUIDs for existing records
                    interviews = Interview.objects.all()
                    for interview in interviews:
                        interview.uuid = uuid.uuid4()
                        interview.save()
                    
                    self.stdout.write("UUID column added and populated")
                    return
                
                # Check for duplicates
                cursor.execute("""
                    SELECT uuid, COUNT(*) 
                    FROM jobapp_interview 
                    WHERE uuid IS NOT NULL 
                    GROUP BY uuid 
                    HAVING COUNT(*) > 1;
                """)
                
                duplicates = cursor.fetchall()
                self.stdout.write(f"Found {len(duplicates)} duplicate UUID groups")
                
                # Fix duplicates
                for duplicate_uuid, count in duplicates:
                    interviews = Interview.objects.filter(uuid=duplicate_uuid)
                    for i, interview in enumerate(interviews):
                        if i > 0:
                            interview.uuid = uuid.uuid4()
                            interview.save()
                
                self.stdout.write(self.style.SUCCESS('UUID fix completed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))