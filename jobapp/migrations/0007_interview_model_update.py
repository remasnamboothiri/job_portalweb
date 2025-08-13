# Generated manually to handle Interview model changes

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0006_auto_20250812_1540'),
    ]

    operations = [
        # First, drop the old Interview model completely
        migrations.DeleteModel(
            name='Interview',
        ),
        
        # Create the new Interview model with the correct structure
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobapp.job')),
                ('candidate_name', models.CharField(default='Unknown Candidate', max_length=255)),
                ('candidate_email', models.EmailField(default='unknown@example.com')),
                ('interview_id', models.CharField(blank=True, max_length=11, unique=True)),
                ('interview_link', models.URLField(blank=True, max_length=500)),
                ('interview_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]