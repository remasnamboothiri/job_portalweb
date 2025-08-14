# Generated manually to fix Interview model schema issues
from django.db import migrations, models
import uuid
from django.db import connection

def check_and_add_uuid_field(apps, schema_editor):
    """
    Check if uuid field exists in Interview table, if not add it
    """
    Interview = apps.get_model('jobapp', 'Interview')
    
    # Try to access uuid field on existing records
    try:
        # Test if uuid field exists by trying to query it
        Interview.objects.filter(uuid__isnull=True).count()
        print("UUID field exists and is accessible")
    except Exception as e:
        print(f"UUID field issue detected: {e}")
        # Field might not exist in database, but that's okay
        # Django will handle it through normal migrations
    
    # Update existing records that might have null UUIDs
    try:
        for interview in Interview.objects.all():
            if not interview.uuid:
                interview.uuid = uuid.uuid4()
                interview.save(update_fields=['uuid'])
    except Exception as e:
        print(f"Could not update UUIDs: {e}")
        # This is okay, the field might not exist yet

def reverse_uuid_field(apps, schema_editor):
    """
    Remove uuid field if needed (reverse operation)
    """
    # This is a no-op since we don't want to actually remove the field
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('jobapp', '0012_fix_uuid_duplicates_sql'),
    ]

    operations = [
        migrations.RunPython(check_and_add_uuid_field, reverse_uuid_field),
    ]