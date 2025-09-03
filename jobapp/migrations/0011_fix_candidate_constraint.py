# Fix candidate_id constraint in interview table

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0010_update_candidate_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='candidate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]