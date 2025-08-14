# Migration to fix Interview model candidate field
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('jobapp', '0014_ensure_interview_uuid'),
    ]

    operations = [
        # Ensure the candidate field exists and is properly configured
        migrations.AlterField(
            model_name='interview',
            name='candidate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]