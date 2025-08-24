from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from .views import get_csrf_token

def api_test(request):
    return JsonResponse({
        'status': 'success',
        'message': 'Django backend is running!',
        'available_endpoints': [
            '/api/accounts/pricing/',
            '/api/accounts/signup/',
            '/api/accounts/login/',
            '/api/dashboard/data/',
            '/api/ranking/',
            '/api/get-csrf-token/',
            '/admin/'
        ]
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test/', api_test, name='api_test'),
    path('api/accounts/', include('accounts.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/ranking/', include('ranking_service.api.urls')),
    path('api/get-csrf-token/', get_csrf_token, name='get-csrf-token'),
] 