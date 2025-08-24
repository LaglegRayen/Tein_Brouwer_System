from django.db import models
from django.contrib.auth.models import User


class PricingPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)  # basic, pro, enterprise
    stripe_price_id = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField()  # Amount in cents
    currency = models.CharField(max_length=3, default='usd')
    interval = models.CharField(max_length=20, default='month')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - ${self.amount/100:.2f}/{self.interval}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    pricing_plan = models.CharField(max_length=50, blank=True, null=True)  # basic, pro, enterprise
    subscription_status = models.CharField(max_length=50, default='inactive')
    # Business info for ranking defaults
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_lat = models.FloatField(blank=True, null=True)
    business_lng = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.subscription_status}" 