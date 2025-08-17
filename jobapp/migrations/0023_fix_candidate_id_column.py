from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0022_fix_interview_candidate_field'),
    ]

    operations = [
        # First, remove any existing foreign key constraints
        migrations.RunSQL(
            "ALTER TABLE jobapp_interview DROP CONSTRAINT IF EXISTS jobapp_interview_candidate_id_fkey;",
            reverse_sql="-- No reverse operation needed"
        ),
        
        # Add candidate_id column if it doesn't exist
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='jobapp_interview' AND column_name='candidate_id') THEN
                    ALTER TABLE jobapp_interview ADD COLUMN candidate_id INTEGER;
                END IF;
            END $$;
            """,
            reverse_sql="ALTER TABLE jobapp_interview DROP COLUMN IF EXISTS candidate_id;"
        ),
        
        # Add the foreign key constraint
        migrations.RunSQL(
            """
            ALTER TABLE jobapp_interview 
            ADD CONSTRAINT jobapp_interview_candidate_id_fkey 
            FOREIGN KEY (candidate_id) REFERENCES jobapp_customuser(id) ON DELETE SET NULL;
            """,
            reverse_sql="ALTER TABLE jobapp_interview DROP CONSTRAINT IF EXISTS jobapp_interview_candidate_id_fkey;"
        ),
    ]