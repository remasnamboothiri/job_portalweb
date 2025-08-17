#!/usr/bin/env python
"""
Create a proper migration for the Interview model
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
import logging

logger = logging.getLogger(__name__)

def create_interview_migration():
    """Create and apply migration for Interview model"""
    try:
        print("🔄 Creating migration for Interview model...")
        
        # Create migration
        call_command('makemigrations', 'jobapp', verbosity=2)
        
        print("🔄 Applying migrations...")
        
        # Apply migrations
        call_command('migrate', verbosity=2)
        
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def check_interview_table():
    """Check the current state of the interview table"""
    try:
        with connection.cursor() as cursor:
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'jobapp_interview'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                print("✅ Interview table exists")
                
                # Check columns
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'jobapp_interview'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                
                print("📋 Current columns:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
                    
                # Check for foreign key constraints
                cursor.execute("""
                    SELECT 
                        tc.constraint_name, 
                        kcu.column_name, 
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name 
                    FROM information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name = 'jobapp_interview';
                """)
                fks = cursor.fetchall()
                
                print("🔗 Foreign key constraints:")
                for fk in fks:
                    print(f"  - {fk[1]} -> {fk[2]}.{fk[3]}")
                    
            else:
                print("❌ Interview table does not exist")
                
        return table_exists
        
    except Exception as e:
        print(f"❌ Error checking interview table: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Starting Interview Migration Process...")
    
    # Check current state
    print("\n📋 Checking current table state...")
    check_interview_table()
    
    # Create and apply migration
    print("\n🔄 Creating migration...")
    if create_interview_migration():
        print("\n📋 Checking table state after migration...")
        check_interview_table()
    
    print("\n✅ Process completed!")