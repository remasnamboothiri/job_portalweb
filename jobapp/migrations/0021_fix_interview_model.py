# Generated migration for Interview model fix

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0001_initial'),  # Adjust this to your latest migration
    ]

    operations = [
        # Ensure Interview table has correct structure
        migrations.RunSQL(
            """
            -- Create interview table if it doesn't exist
            CREATE TABLE IF NOT EXISTS jobapp_interview (
                id SERIAL PRIMARY KEY,
                uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                job_position_id INTEGER NOT NULL,
                candidate_id INTEGER,
                candidate_name VARCHAR(255) DEFAULT 'Unknown Candidate',
                candidate_email VARCHAR(254) DEFAULT 'unknown@example.com',
                interview_id VARCHAR(11) UNIQUE,
                interview_link VARCHAR(500),
                interview_date TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Add foreign key constraints if they don't exist
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_name = 'jobapp_interview_job_position_id_fkey'
                ) THEN
                    ALTER TABLE jobapp_interview 
                    ADD CONSTRAINT jobapp_interview_job_position_id_fkey 
                    FOREIGN KEY (job_position_id) REFERENCES jobapp_job(id) ON DELETE CASCADE;
                END IF;
                
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
            reverse_sql="DROP TABLE IF EXISTS jobapp_interview CASCADE;"
        ),
    ]
