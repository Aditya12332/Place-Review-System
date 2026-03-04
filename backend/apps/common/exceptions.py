from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Consistent error response format."""
    response = exception_handler(exc, context)

    if response is not None:
        # Wrap DRF errors
        original_data = response.data
        response.data = {
            'error': True,
            'message': _extract_message(original_data),
            'details': original_data,
        }
    else:
        logger.error(f"Unhandled exception in {context.get('view')}: {exc}", exc_info=True)
        return Response({
            'error': True,
            'message': 'An unexpected error occurred',
            'details': str(exc) if __debug__ else None,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def _extract_message(data):
    """Best-effort human readable message from DRF error data."""
    if isinstance(data, dict):
        for key in ('detail', 'message', 'non_field_errors'):
            if key in data:
                val = data[key]
                if isinstance(val, list):
                    return str(val[0])
                return str(val)
        # Return first field error
        for key, val in data.items():
            if isinstance(val, list) and val:
                return f"{key}: {val[0]}"
            if isinstance(val, str):
                return f"{key}: {val}"
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)