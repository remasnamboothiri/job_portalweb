# Generated migration to add missing uuid column
from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0015_fix_interview_candidate_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True),
        ),
    ]