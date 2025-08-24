from django.contrib import admin
from .models import UserProfile, PricingPlan


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount_display', 'currency', 'interval', 'stripe_price_id', 'created_at']
    list_filter = ['currency', 'interval', 'created_at']
    search_fields = ['name', 'stripe_price_id']
    readonly_fields = ['created_at', 'updated_at']
    
    def amount_display(self, obj):
        return f"${obj.amount/100:.2f}"
    amount_display.short_description = 'Amount'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'pricing_plan', 'subscription_status', 'stripe_customer_id', 'created_at']
    list_filter = ['subscription_status', 'pricing_plan', 'created_at']
    search_fields = ['user__email', 'stripe_customer_id', 'pricing_plan']
    readonly_fields = ['stripe_customer_id', 'stripe_subscription_id', 'stripe_price_id', 'created_at', 'updated_at'] 