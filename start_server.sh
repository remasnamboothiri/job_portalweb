#!/bin/bash

# Start server script with proper timeout configuration
echo "Starting Django server with Gunicorn..."

# Set environment variables
export DJANGO_SETTINGS_MODULE=job_platform.settings

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn with configuration
echo "Starting Gunicorn server..."
gunicorn job_platform.wsgi:application \
    --config gunicorn.conf.py \
    --timeout 60 \
    --workers 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --bind 0.0.0.0:8000