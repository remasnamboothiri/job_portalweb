# Fix UUID field properly by handling duplicates
from django.db import migrations, models
import uuid

def generate_unique_uuids(apps, schema_editor):
    Interview = apps.get_model('jobapp', 'Interview')
    for interview in Interview.objects.all():
        interview.uuid = uuid.uuid4()
        interview.save()

def reverse_uuid_fix(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0016_add_uuid_column'),
    ]

    operations = [
        # First, populate existing records with unique UUIDs
        migrations.RunPython(generate_unique_uuids, reverse_uuid_fix),
        
        # Then make the field unique and non-null
        migrations.AlterField(
            model_name='interview',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]