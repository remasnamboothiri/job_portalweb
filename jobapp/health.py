import logging
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from decouple import config

logger = logging.getLogger(__name__)

def health_check(request):
    """Health check endpoint for monitoring"""
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Environment variables check
    required_vars = ['SECRET_KEY', 'DATABASE_URL', 'NVIDIA_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        try:
            value = config(var)
            if not value:
                missing_vars.append(var)
        except:
            missing_vars.append(var)
    
    if missing_vars:
        health_status['checks']['environment'] = f'missing: {", ".join(missing_vars)}'
        health_status['status'] = 'degraded'
    else:
        health_status['checks']['environment'] = 'healthy'
    
    # AI API check (basic)
    try:
        nvidia_key = config('NVIDIA_API_KEY', default='')
        if nvidia_key:
            health_status['checks']['ai_api'] = 'configured'
        else:
            health_status['checks']['ai_api'] = 'not_configured'
            health_status['status'] = 'degraded'
    except:
        health_status['checks']['ai_api'] = 'error'
        health_status['status'] = 'degraded'
    
    # Return appropriate status code
    status_code = 200
    if health_status['status'] == 'unhealthy':
        status_code = 503
    elif health_status['status'] == 'degraded':
        status_code = 200  # Still operational
    
    return JsonResponse(health_status, status=status_code)

def readiness_check(request):
    """Readiness check for deployment"""
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
        
        return JsonResponse({
            'status': 'ready',
            'migrations': migration_count,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=503)