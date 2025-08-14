from django.db import migrations
import uuid

def fix_uuid_duplicates_sql(apps, schema_editor):
    Interview = apps.get_model('jobapp', 'Interview')
    
    # Get all interviews with duplicate UUIDs
    seen_uuids = set()
    interviews_to_update = []
    
    for interview in Interview.objects.all():
        if interview.uuid is None or interview.uuid in seen_uuids:
            interviews_to_update.append(interview)
        else:
            seen_uuids.add(interview.uuid)
    
    # Update duplicates with new UUIDs
    for interview in interviews_to_update:
        interview.uuid = uuid.uuid4()
        interview.save()

def reverse_fix_uuid_duplicates_sql(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('jobapp', '0011_fix_duplicate_uuids'),
    ]

    operations = [
        migrations.RunPython(fix_uuid_duplicates_sql, reverse_fix_uuid_duplicates_sql),
    ]