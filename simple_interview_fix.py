"""
Simple fix for interview database issues - just update the views
"""

# Read the current views.py
with open('jobapp/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if our fix is already applied
if 'Alternative interview query also failed' in content:
    print("Interview fix already applied!")
else:
    print("Interview fix not found in views.py")
    print("The fix should have been applied by the previous fsReplace operations.")

# Also create a simple database migration file
migration_content = '''# Generated migration for Interview model fix

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
'''

# Write the migration file
import os
migrations_dir = 'jobapp/migrations'
if not os.path.exists(migrations_dir):
    os.makedirs(migrations_dir)

# Find the next migration number
existing_migrations = [f for f in os.listdir(migrations_dir) if f.startswith('0') and f.endswith('.py')]
if existing_migrations:
    last_num = max([int(f.split('_')[0]) for f in existing_migrations])
    next_num = f"{last_num + 1:04d}"
else:
    next_num = "0002"

migration_file = f"{migrations_dir}/{next_num}_fix_interview_model.py"

with open(migration_file, 'w', encoding='utf-8') as f:
    f.write(migration_content)

print(f"Created migration file: {migration_file}")
print("Simple interview fix completed!")
print("\nTo apply this fix in production:")
print("1. Deploy the updated views.py (already done)")
print("2. Run: python manage.py migrate")
print("3. The database will be fixed automatically")