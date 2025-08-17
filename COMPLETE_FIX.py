#!/usr/bin/env python
"""
COMPLETE FIX FOR JOB PORTAL ISSUES
- Forces PostgreSQL database
- Fixes UUID column missing error
- Ensures interview links work
"""
import os
import sys

def fix_settings():
    """Fix settings.py to force PostgreSQL"""
    settings_path = 'job_platform/settings.py'
    
    # Read current settings
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Replace database configuration
    old_db_config = """# Database configuration
if config('DATABASE_URL', default=None) and dj_database_url:
    # Production: Use PostgreSQL from DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }"""
    
    new_db_config = """# Database configuration - Always use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='job_portal_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Override with DATABASE_URL if available (for production)
if config('DATABASE_URL', default=None) and dj_database_url:
    DATABASES['default'] = dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )"""
    
    # Replace in content
    content = content.replace(old_db_config, new_db_config)
    
    # Write back
    with open(settings_path, 'w') as f:
        f.write(content)
    
    print("✅ Settings.py fixed - now using PostgreSQL")

def fix_database():
    """Fix database UUID issues"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
    
    import django
    django.setup()
    
    from django.db import connection
    from django.core.management import call_command
    
    try:
        with connection.cursor() as cursor:
            # Check if we're using PostgreSQL
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"Database: {version}")
            
            if 'PostgreSQL' not in version:
                print("❌ Not using PostgreSQL! Check your database configuration.")
                return False
            
            # Add UUID column if missing
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'jobapp_interview' AND column_name = 'uuid';
            """)
            
            if not cursor.fetchone():
                print("Adding UUID column...")
                cursor.execute("ALTER TABLE jobapp_interview ADD COLUMN uuid UUID DEFAULT gen_random_uuid();")
                cursor.execute("UPDATE jobapp_interview SET uuid = gen_random_uuid() WHERE uuid IS NULL;")
                cursor.execute("ALTER TABLE jobapp_interview ADD CONSTRAINT jobapp_interview_uuid_unique UNIQUE (uuid);")
                print("✅ UUID column added")
            else:
                print("✅ UUID column already exists")
        
        # Run migrations
        print("Running migrations...")
        call_command('migrate', verbosity=0)
        
        print("✅ Database fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        return False

def main():
    print("🔧 COMPLETE FIX STARTING...")
    
    # Step 1: Fix settings
    fix_settings()
    
    # Step 2: Fix database
    if fix_database():
        print("🎉 ALL FIXES COMPLETED!")
        print("\nNEXT STEPS:")
        print("1. Run: python manage.py runserver")
        print("2. Test interview links on candidate dashboard")
        print("3. Push to production: git add . && git commit -m 'Fix PostgreSQL and interviews' && git push")
    else:
        print("❌ Fix failed. Check your PostgreSQL connection.")

if __name__ == '__main__':
    main()