# Fix candidate_id constraint using raw SQL

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0011_fix_candidate_constraint'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE jobapp_interview ALTER COLUMN candidate_id DROP NOT NULL;",
            reverse_sql="ALTER TABLE jobapp_interview ALTER COLUMN candidate_id SET NOT NULL;"
        ),
    ]