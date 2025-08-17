from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0023_fix_candidate_id_column'),
    ]

    operations = [
        # Add candidate_id column directly with SQL
        migrations.RunSQL(
            """
            ALTER TABLE jobapp_interview 
            ADD COLUMN IF NOT EXISTS candidate_id INTEGER;
            """,
            reverse_sql="ALTER TABLE jobapp_interview DROP COLUMN IF EXISTS candidate_id;"
        ),
        
        # Add foreign key constraint
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_name = 'jobapp_interview_candidate_id_fkey'
                ) THEN
                    ALTER TABLE jobapp_interview 
                    ADD CONSTRAINT jobapp_interview_candidate_id_fkey 
                    FOREIGN KEY (candidate_id) REFERENCES jobapp_customuser(id) ON DELETE SET NULL;
                END IF;
            END $$;
            """,
            reverse_sql="ALTER TABLE jobapp_interview DROP CONSTRAINT IF EXISTS jobapp_interview_candidate_id_fkey;"
        ),
    ]