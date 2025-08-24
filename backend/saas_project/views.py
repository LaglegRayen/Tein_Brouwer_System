"""
Common views for the project
"""

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET


@require_GET
def get_csrf_token(request):
    """
    Return a new CSRF token
    """
    token = get_token(request)
    response = JsonResponse({
        'csrfToken': token,
        'message': 'CSRF token generated successfully'
    })
    response['X-CSRFToken'] = token
    return response
