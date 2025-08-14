# Migration to ensure Interview model has uuid field
from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ('jobapp', '0013_fix_interview_schema'),
    ]

    operations = [
        # This migration ensures the uuid field exists and is properly configured
        migrations.AlterField(
            model_name='interview',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, editable=False, null=True, unique=True),
        ),
    ]