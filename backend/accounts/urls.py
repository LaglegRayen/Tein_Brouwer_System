from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('check-auth/', views.check_auth, name='check_auth'),
    path('pricing/', views.get_pricing_plans, name='pricing'),
] 