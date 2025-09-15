import logging
import json
from django.http import JsonResponse, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class TimeoutHandlingMiddleware(MiddlewareMixin):
    """Middleware to handle timeout errors gracefully"""
    
    def process_exception(self, request, exception):
        """Handle timeout and connection errors"""
        
        # Check if it's a timeout or connection error
        if isinstance(exception, (TimeoutError, ConnectionError)):
            logger.error(f"Timeout/Connection error: {str(exception)}")
            
            # For AJAX requests, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Request timed out. Please try again.',
                    'response': 'The request took too long to process. Please try again in a moment.',
                    'success': False,
                    'timeout': True
                }, status=504)
            
            # For regular requests, return HTML response
            return HttpResponse(
                'Request timed out. Please refresh the page and try again.',
                status=504
            )
        
        # Check for NVIDIA API specific errors
        if 'nvidia' in str(exception).lower() or 'api' in str(exception).lower():
            logger.error(f"API error: {str(exception)}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'AI service temporarily unavailable.',
                    'response': 'Our AI service is temporarily unavailable. Please try again in a moment.',
                    'success': False,
                    'api_error': True
                }, status=503)
        
        # Let other exceptions be handled normally
        return None

class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log slow requests"""
    
    def process_request(self, request):
        """Log request start time"""
        import time
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log request completion time"""
        if hasattr(request, '_start_time'):
            import time
            duration = time.time() - request._start_time
            
            # Log slow requests (over 10 seconds)
            if duration > 10:
                logger.warning(f"Slow request: {request.path} took {duration:.2f} seconds")
            
            # Log very slow requests (over 30 seconds)
            if duration > 30:
                logger.error(f"Very slow request: {request.path} took {duration:.2f} seconds")
        
        return response