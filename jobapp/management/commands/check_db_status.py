from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

class Command(BaseCommand):
    help = 'Check database configuration and status'

    def handle(self, *args, **options):
        db_config = settings.DATABASES['default']
        
        self.stdout.write(f"Database Engine: {db_config['ENGINE']}")
        self.stdout.write(f"Database Name: {db_config.get('NAME', 'N/A')}")
        
        try:
            with connection.cursor() as cursor:
                if 'postgresql' in db_config['ENGINE']:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    self.stdout.write(f"PostgreSQL Version: {version}")
                    
                    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'jobapp_interview';")
                    table_exists = cursor.fetchone()
                    
                    if table_exists:
                        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'jobapp_interview' AND column_name = 'uuid';")
                        uuid_exists = cursor.fetchone()
                        self.stdout.write(f"Interview table UUID column: {'EXISTS' if uuid_exists else 'MISSING'}")
                    else:
                        self.stdout.write("Interview table: NOT FOUND")
                        
                else:
                    cursor.execute("SELECT sqlite_version();")
                    version = cursor.fetchone()[0]
                    self.stdout.write(f"SQLite Version: {version}")
                    
            self.stdout.write(self.style.SUCCESS("Database connection: OK"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Database error: {e}"))