# Production Deployment Steps

## Current Issue
Your production environment is using PostgreSQL but missing the UUID column in the `jobapp_interview` table, causing these errors:
```
column jobapp_interview.uuid does not exist
```

## What I Fixed

### 1. Database Configuration ✅
- Fixed `settings.py` to properly use PostgreSQL in production
- Added fallback to SQLite for development

### 2. Production Migration ✅
- Created `0019_ensure_uuid_production.py` for safe PostgreSQL migration
- Handles existing data properly

### 3. Management Commands ✅
- `fix_production_db` - Direct database schema fix
- `check_db_status` - Check current database status
- `test_db` - Test database operations

### 4. Static Files ✅
- Fixed missing font files (icomoon, line-icons)
- Added favicon support
- Updated URL patterns

## Deploy to Production

### Step 1: Push Changes
```bash
git add .
git commit -m "Fix PostgreSQL database schema and static files"
git push origin main
```

### Step 2: In Production Environment
After deployment, run these commands in your production environment:

```bash
# Check current database status
python check_db_status.py

# Run migrations (this will add the UUID column)
python manage.py migrate

# Fix any remaining database issues
python manage.py fix_production_db

# Collect static files
python manage.py collectstatic --noinput

# Test the database
python manage.py test_db
```

### Step 3: Alternative - Use Deployment Script
Or run the automated script:
```bash
python deploy_production.py
```

## Expected Results After Fix

### ✅ Database Errors Gone
- No more "column jobapp_interview.uuid does not exist" errors
- Interview dashboard loads without warnings

### ✅ Static Files Working
- Font files load correctly (no more 404s)
- Favicon loads
- All CSS and JS files work

### ✅ Application Functional
- Users can login and access dashboards
- Interview functionality works
- All features operational

## Environment Variables Required
Make sure these are set in your production environment:
```
DATABASE_URL=postgresql://user:password@host:port/database
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=job-portal-23qb.onrender.com,.onrender.com
```

## Verification Commands
After deployment, check these:

```bash
# 1. Check database status
python check_db_status.py

# 2. Test database operations
python manage.py test_db

# 3. Check for any remaining errors in logs
# Look for these success indicators:
# - [OK] Using PostgreSQL
# - [OK] UUID column exists
# - [INFO] Interview records: X
```

## If Issues Persist

### Manual PostgreSQL Fix
If migrations fail, run this SQL directly on your PostgreSQL database:
```sql
-- Check if UUID column exists
SELECT column_name FROM information_schema.columns 
WHERE table_name='jobapp_interview' AND column_name='uuid';

-- If not exists, add it:
ALTER TABLE jobapp_interview ADD COLUMN uuid UUID DEFAULT gen_random_uuid();
UPDATE jobapp_interview SET uuid = gen_random_uuid() WHERE uuid IS NULL;
ALTER TABLE jobapp_interview ALTER COLUMN uuid SET NOT NULL;
CREATE UNIQUE INDEX jobapp_interview_uuid_unique ON jobapp_interview(uuid);
```

## Files Modified/Added
- `settings.py` - Fixed database configuration
- `0019_ensure_uuid_production.py` - Production migration
- `fix_production_db.py` - Database fix command
- `check_db_status.py` - Status checker
- `deploy_production.py` - Deployment automation
- Static files - Added missing fonts and favicon

Your PostgreSQL database will be properly configured after following these steps!