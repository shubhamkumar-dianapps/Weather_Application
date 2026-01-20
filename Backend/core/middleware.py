from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class GracefulExceptionMiddleware:
    """
    Middleware to catch exceptions that would otherwise cause a 500 server error crash
    and return a clean JSON response instead, without dumping a traceback to the console.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Handle 404s for API/Auth routes to prevent HTML leakage
        if response.status_code == 404 and (request.path.startswith('/api/') or request.path.startswith('/auth/')):
             return JsonResponse({'error': 'Resource not found', 'path': request.path}, status=404)
        
        return response

    def process_exception(self, request, exception):
        # Specific handling for the "APPEND_SLASH" RuntimeError
        if isinstance(exception, RuntimeError) and "URL doesn't end in a slash" in str(exception):
            return JsonResponse({
                'error': 'Missing trailing slash in URL. Please append "/" to your request path.'
            }, status=400)

        # Generic handling for other unhandled exceptions
        logger.error(f'Unhandled Exception: {exception}', exc_info=True)
        
        return JsonResponse({
            'error': 'Internal Server Error',
            'detail': 'An unexpected error occurred. Please contact support.' 
        }, status=500)
