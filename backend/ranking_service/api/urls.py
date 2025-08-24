"""
URL patterns for the ranking service API
"""

from django.urls import path
from . import views

app_name = 'ranking_service'

urlpatterns = [
    # Complete workflow
    path('grid-check/', views.run_grid_check, name='grid_check'),
    
    # Split workflow
    path('create-tasks/', views.create_tasks, name='create_tasks'),
    path('get-results/', views.get_results, name='get_results'),
    
    # Status and info
    path('status/', views.get_status, name='status'),
    path('info/', views.service_info, name='info'),
    
    # Convenience endpoints
    path('quick-check/', views.quick_check, name='quick_check'),
    path('history/', views.history, name='history'),
]
