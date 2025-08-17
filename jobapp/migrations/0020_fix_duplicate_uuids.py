# Fix duplicate UUIDs in PostgreSQL
from django.db import migrations
import uuid

def fix_duplicate_uuids(apps, schema_editor):
    Interview = apps.get_model('jobapp', 'Interview')
    
    # Get all interviews
    interviews = Interview.objects.all()
    
    # Track used UUIDs
    used_uuids = set()
    
    for interview in interviews:
        # If UUID is None or duplicate, generate new one
        if not interview.uuid or interview.uuid in used_uuids:
            new_uuid = uuid.uuid4()
            while new_uuid in used_uuids:
                new_uuid = uuid.uuid4()
            interview.uuid = new_uuid
            interview.save()
        
        used_uuids.add(interview.uuid)

def reverse_fix(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0019_ensure_uuid_production'),
    ]

    operations = [
        migrations.RunPython(fix_duplicate_uuids, reverse_fix),
    ]