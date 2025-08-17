import os
import django
import psycopg2
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

def fix_candidate_id_column():
    """Fix the missing candidate_id column in jobapp_interview table"""
    
    # Get database connection details from Django settings
    db_config = settings.DATABASES['default']
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=db_config['HOST'],
            database=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            port=db_config['PORT']
        )
        
        cursor = conn.cursor()
        
        print("Fixing candidate_id column...")
        
        # Check if candidate_id column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='jobapp_interview' AND column_name='candidate_id';
        """)
        
        if not cursor.fetchone():
            print("Adding candidate_id column...")
            cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN candidate_id INTEGER;")
            
            # Add foreign key constraint
            cursor.execute("""
                ALTER TABLE jobapp_interview 
                ADD CONSTRAINT jobapp_interview_candidate_id_fkey 
                FOREIGN KEY (candidate_id) REFERENCES jobapp_customuser(id) ON DELETE SET NULL;
            """)
            
            print("candidate_id column added successfully!")
        else:
            print("candidate_id column already exists!")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database fix completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_candidate_id_column()