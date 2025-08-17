# PostgreSQL Database Fix Guide

## Problem
The production environment is using PostgreSQL but the database schema is missing the UUID column in the `jobapp_interview` table, causing errors like:
```
column jobapp_interview.uuid does not exist
```

## Root Cause
- Local development uses SQLite (which has the UUID column)
- Production uses PostgreSQL (which doesn't have the UUID column)
- Migrations weren't properly applied to the PostgreSQL database

## Solution

### 1. Database Configuration Fixed
Updated `settings.py` to properly detect and use PostgreSQL in production:
```python
# Now properly uses DATABASE_URL for PostgreSQL in production
if config('DATABASE_URL', default=None):
    DATABASES = {'default': dj_database_url.config(...)}
```

### 2. Production Migration Created
Created `0019_ensure_uuid_production.py` that:
- Safely adds UUID column if missing
- Populates existing records with UUIDs
- Works with PostgreSQL's `gen_random_uuid()`

### 3. Management Commands Added
- `fix_production_db.py` - Manually fix database schema
- `test_db.py` - Test database operations
- `check_db_status.py` - Check current database status

### 4. Deployment Script
`deploy_production.py` - Complete deployment automation

## How to Fix Production

### Option 1: Automatic (Recommended)
```bash
# In production environment
python deploy_production.py
```

### Option 2: Manual Steps
```bash
# 1. Check current status
python check_db_status.py

# 2. Run migrations
python manage.py migrate

# 3. Fix database schema
python manage.py fix_production_db

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Test database
python manage.py test_db
```

### Option 3: Direct SQL (PostgreSQL)
If migrations fail, run this SQL directly on PostgreSQL:
```sql
-- Add UUID column if missing
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='jobapp_interview' AND column_name='uuid'
    ) THEN
        ALTER TABLE jobapp_interview ADD COLUMN uuid UUID DEFAULT gen_random_uuid();
        UPDATE jobapp_interview SET uuid = gen_random_uuid() WHERE uuid IS NULL;
        ALTER TABLE jobapp_interview ALTER COLUMN uuid SET NOT NULL;
        CREATE UNIQUE INDEX jobapp_interview_uuid_unique ON jobapp_interview(uuid);
    END IF;
END $$;
```

## Environment Variables Needed
Make sure these are set in production:
```
DATABASE_URL=postgresql://user:password@host:port/database
DEBUG=False
SECRET_KEY=your-secret-key
```

## Verification
After applying fixes, you should see:
- ✅ No more UUID column errors in logs
- ✅ Interview dashboard loads without warnings
- ✅ All static files load (fonts, favicon)

## Files Added/Modified
- `settings.py` - Fixed database configuration
- `0019_ensure_uuid_production.py` - Production migration
- `fix_production_db.py` - Database fix command
- `deploy_production.py` - Deployment script
- `check_db_status.py` - Status checker

## Next Steps
1. Deploy these changes to production
2. Run the deployment script
3. Monitor logs to confirm fixes work
4. Test interview functionality

The application will now properly use PostgreSQL in production with the correct schema.