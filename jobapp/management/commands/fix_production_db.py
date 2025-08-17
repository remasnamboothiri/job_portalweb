from django.core.management.base import BaseCommand
from django.db import connection
import uuid

class Command(BaseCommand):
    help = 'Fix production database schema issues'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # Check if uuid column exists
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='jobapp_interview' AND column_name='uuid';
                """)
                
                uuid_exists = cursor.fetchone()
                
                if not uuid_exists:
                    self.stdout.write("Adding UUID column to Interview table...")
                    
                    # Add UUID column
                    cursor.execute("""
                        ALTER TABLE jobapp_interview 
                        ADD COLUMN uuid UUID DEFAULT gen_random_uuid() UNIQUE;
                    """)
                    
                    # Update existing records with unique UUIDs
                    cursor.execute("""
                        UPDATE jobapp_interview 
                        SET uuid = gen_random_uuid() 
                        WHERE uuid IS NULL;
                    """)
                    
                    # Make UUID column NOT NULL
                    cursor.execute("""
                        ALTER TABLE jobapp_interview 
                        ALTER COLUMN uuid SET NOT NULL;
                    """)
                    
                    self.stdout.write(self.style.SUCCESS('UUID column added successfully'))
                else:
                    self.stdout.write('UUID column already exists')
                
                # Test the fix
                cursor.execute("SELECT COUNT(*) FROM jobapp_interview;")
                count = cursor.fetchone()[0]
                self.stdout.write(f"Interview table has {count} records")
                
                if count > 0:
                    cursor.execute("SELECT uuid FROM jobapp_interview LIMIT 1;")
                    sample_uuid = cursor.fetchone()[0]
                    self.stdout.write(f"Sample UUID: {sample_uuid}")
                
                self.stdout.write(self.style.SUCCESS('Database schema fix completed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fixing database: {e}'))
            # Fallback for non-PostgreSQL databases
            if 'information_schema' not in str(e).lower():
                self.stdout.write('Attempting SQLite fallback...')
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("PRAGMA table_info(jobapp_interview);")
                        columns = [row[1] for row in cursor.fetchall()]
                        
                        if 'uuid' not in columns:
                            cursor.execute("""
                                ALTER TABLE jobapp_interview 
                                ADD COLUMN uuid TEXT;
                            """)
                            
                            # Update with UUIDs
                            from jobapp.models import Interview
                            for interview in Interview.objects.all():
                                interview.uuid = uuid.uuid4()
                                interview.save()
                            
                            self.stdout.write(self.style.SUCCESS('SQLite UUID column added'))
                        else:
                            self.stdout.write('UUID column already exists in SQLite')
                            
                except Exception as e2:
                    self.stdout.write(self.style.ERROR(f'SQLite fallback failed: {e2}'))