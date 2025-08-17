import os
import django
import psycopg2
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

def fix_interview_table():
    """Comprehensive fix for the Interview table"""
    
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
        
        print("Fixing Interview table schema...")
        
        # Check existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='jobapp_interview'
            ORDER BY column_name;
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Required columns for the Interview model
        required_columns = {
            'candidate_id': 'INTEGER',
            'created_at': 'TIMESTAMP WITH TIME ZONE',
            'uuid': 'UUID',
            'job_position_id': 'INTEGER',
            'candidate_name': 'VARCHAR(255)',
            'candidate_email': 'VARCHAR(254)',
            'interview_id': 'VARCHAR(11)',
            'interview_link': 'VARCHAR(500)',
            'interview_date': 'TIMESTAMP WITH TIME ZONE'
        }
        
        # Add missing columns
        for column, data_type in required_columns.items():
            if column not in existing_columns:
                print(f"Adding missing column: {column}")
                
                if column == 'created_at':
                    cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {column} {data_type} DEFAULT NOW();")
                elif column == 'uuid':
                    cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {column} {data_type} DEFAULT gen_random_uuid();")
                elif column == 'candidate_name':
                    cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {column} {data_type} DEFAULT 'Unknown Candidate';")
                elif column == 'candidate_email':
                    cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {column} {data_type} DEFAULT 'unknown@example.com';")
                elif column == 'interview_id':
                    cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {column} {data_type} DEFAULT '';")
                elif column == 'interview_link':
                    cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {column} {data_type} DEFAULT '';")
                else:
                    cursor.execute(f"ALTER TABLE jobapp_interview ADD COLUMN {column} {data_type};")
        
        # Add foreign key constraints if they don't exist
        print("Checking foreign key constraints...")
        
        # Check if candidate_id foreign key exists
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name='jobapp_interview' 
            AND constraint_type='FOREIGN KEY'
            AND constraint_name LIKE '%candidate_id%';
        """)
        
        if not cursor.fetchone():
            print("Adding candidate_id foreign key constraint...")
            cursor.execute("""
                ALTER TABLE jobapp_interview 
                ADD CONSTRAINT jobapp_interview_candidate_id_fkey 
                FOREIGN KEY (candidate_id) REFERENCES jobapp_customuser(id) ON DELETE SET NULL;
            """)
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Interview table fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    fix_interview_table()