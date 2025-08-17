# Ensure UUID field exists in production
from django.db import migrations, models, connection
import uuid

def add_uuids_to_existing_interviews(apps, schema_editor):
    Interview = apps.get_model('jobapp', 'Interview')
    for interview in Interview.objects.all():
        if not interview.uuid:
            interview.uuid = uuid.uuid4()
            interview.save()

def ensure_uuid_column(apps, schema_editor):
    # Check if we're using PostgreSQL
    if 'postgresql' in connection.settings_dict['ENGINE']:
        with connection.cursor() as cursor:
            # Check if UUID column exists
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='jobapp_interview' AND column_name='uuid';
            """)
            
            if not cursor.fetchone():
                # Add UUID column for PostgreSQL
                cursor.execute("""
                    ALTER TABLE jobapp_interview ADD COLUMN uuid UUID DEFAULT gen_random_uuid();
                """)
                cursor.execute("""
                    UPDATE jobapp_interview SET uuid = gen_random_uuid() WHERE uuid IS NULL;
                """)

def reverse_uuid_addition(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0018_fix_uuid_properly'),
    ]

    operations = [
        # Ensure UUID column exists (PostgreSQL only)
        migrations.RunPython(ensure_uuid_column, reverse_uuid_addition),
        
        # Populate UUIDs for existing records
        migrations.RunPython(add_uuids_to_existing_interviews, reverse_uuid_addition),
    ]