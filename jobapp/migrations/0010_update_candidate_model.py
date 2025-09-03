# Generated migration for updated Candidate model

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0009_remove_duplicate_candidates'),
    ]

    operations = [
        # Remove job field from Candidate model
        migrations.RemoveField(
            model_name='candidate',
            name='job',
        ),
        
        # Add unique constraint for email and added_by
        migrations.AlterUniqueTogether(
            name='candidate',
            unique_together={('email', 'added_by')},
        ),
    ]