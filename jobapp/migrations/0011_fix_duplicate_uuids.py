from django.db import migrations
import uuid

def fix_duplicate_uuids(apps, schema_editor):
    Interview = apps.get_model('jobapp', 'Interview')
    
    # Find all interviews with duplicate or null UUIDs
    interviews = Interview.objects.all()
    
    for interview in interviews:
        # Generate new UUID for each interview
        interview.uuid = uuid.uuid4()
        interview.save()

def reverse_fix_duplicate_uuids(apps, schema_editor):
    # This is irreversible
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('jobapp', '0010_interview_candidate_interview_created_at_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_duplicate_uuids, reverse_fix_duplicate_uuids),
    ]