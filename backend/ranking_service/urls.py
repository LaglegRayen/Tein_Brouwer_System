"""
Main URL configuration for the ranking service
"""

from django.urls import path, include

urlpatterns = [
    path('api/', include('ranking_service.api.urls')),
]
