# Data migration to remove duplicate candidates

from django.db import migrations

def remove_duplicate_candidates(apps, schema_editor):
    Candidate = apps.get_model('jobapp', 'Candidate')
    
    # Find duplicates based on email and added_by
    seen = set()
    duplicates = []
    
    for candidate in Candidate.objects.all().order_by('added_at'):
        key = (candidate.email, candidate.added_by_id)
        if key in seen:
            duplicates.append(candidate.id)
        else:
            seen.add(key)
    
    # Delete duplicates (keeping the first one)
    if duplicates:
        Candidate.objects.filter(id__in=duplicates).delete()
        print(f"Removed {len(duplicates)} duplicate candidates")

def reverse_remove_duplicates(apps, schema_editor):
    # This is irreversible
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0008_interview_candidate_phone_interview_status'),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_candidates, reverse_remove_duplicates),
    ]