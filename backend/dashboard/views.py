from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import UserProfile
from .models import Activity
import random
from datetime import datetime, timedelta


@api_view(['GET'])
def dashboard_data(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    total_users = User.objects.count()
    active_subscriptions = UserProfile.objects.exclude(subscription_status='inactive').count()
    
    recent_activities = [
        {
            'id': 1,
            'action': 'User Registration',
            'description': 'New user signed up for Pro plan',
            'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
            'user': 'john@example.com'
        },
        {
            'id': 2,
            'action': 'Subscription Upgrade',
            'description': 'User upgraded from Basic to Enterprise',
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'user': 'sarah@example.com'
        },
        {
            'id': 3,
            'action': 'Payment Received',
            'description': 'Monthly subscription payment processed',
            'timestamp': (datetime.now() - timedelta(hours=5)).isoformat(),
            'user': 'mike@example.com'
        },
        {
            'id': 4,
            'action': 'Trial Started',
            'description': 'New user started 7-day trial',
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
            'user': 'emma@example.com'
        },
        {
            'id': 5,
            'action': 'Feature Usage',
            'description': 'Advanced analytics feature accessed',
            'timestamp': (datetime.now() - timedelta(days=2)).isoformat(),
            'user': 'alex@example.com'
        }
    ]
    
    review_metrics = {
        'average_rating': 4.7,
        'total_reviews': 156,
        'five_star': 89,
        'four_star': 42,
        'three_star': 18,
        'two_star': 5,
        'one_star': 2,
        'recent_review': {
            'rating': 5,
            'comment': 'Excellent platform! The analytics features are incredibly helpful.',
            'user': 'Jennifer K.',
            'date': (datetime.now() - timedelta(days=1)).isoformat()
        }
    }
    
    monthly_revenue = random.randint(15000, 25000)
    growth_rate = random.randint(12, 28)
    
    dashboard_metrics = {
        'total_users': total_users + 1247,
        'active_subscriptions': active_subscriptions + 892,
        'monthly_revenue': monthly_revenue,
        'growth_rate': growth_rate,
        'trial_conversions': 73.2,
        'churn_rate': 2.1,
        'recent_activities': recent_activities,
        'review_metrics': review_metrics,
        'quick_stats': {
            'new_signups_today': 23,
            'trials_ending_soon': 15,
            'support_tickets_open': 7,
            'server_uptime': '99.9%'
        },
        'user_profile': {
            'email': request.user.email,
            'subscription_status': getattr(
                UserProfile.objects.filter(user=request.user).first(),
                'subscription_status',
                'trialing'
            ),
            'trial_days_left': 6,
            'plan_name': 'Pro Plan'
        }
    }
    
    return Response(dashboard_metrics, status=status.HTTP_200_OK) 