from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'error': True,
            'message': str(exc),
            'details': response.data
        }
        response.data = custom_response
    else:
        # Log unhandled exceptions
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return Response({
            'error': True,
            'message': 'An unexpected error occurred',
            'details': str(exc)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response