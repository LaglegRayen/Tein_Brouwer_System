import os
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from .models import UserProfile, PricingPlan
from .serializers import SignupSerializer, LoginSerializer, UserProfileSerializer



class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Skip CSRF check


PRICING_PLANS = {
    'basic': {'price_id': 'price_basic_test', 'amount': 999},
    'pro': {'price_id': 'price_pro_test', 'amount': 1999},
    'enterprise': {'price_id': 'price_enterprise_test', 'amount': 4999},
}


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        pricing_plan = serializer.validated_data['pricing_plan']
        
        user = None
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            
            # Check if Stripe is properly configured by checking environment variables directly
            stripe_secret_from_env = os.getenv('STRIPE_SECRET_KEY')
            stripe_publishable_from_env = os.getenv('STRIPE_PUBLISHABLE_KEY')
            
            stripe_configured = (
                stripe_secret_from_env and 
                stripe_publishable_from_env and
                stripe_secret_from_env != 'sk_test_your_secret_key_here' and
                stripe_secret_from_env != 'sk_test_placeholder_for_development' and
                stripe_secret_from_env.startswith('sk_') and
                stripe_publishable_from_env.startswith('pk_')
            )
            
            print(f"🔍 Stripe secret from env: {stripe_secret_from_env}")
            print(f"🔍 Stripe publishable from env: {stripe_publishable_from_env}")
            print(f"🔍 Stripe configured: {stripe_configured}")
            print(f"🔍 Settings Stripe secret: {settings.STRIPE_SECRET_KEY}")
            print(f"🔍 Settings Stripe publishable: {settings.STRIPE_PUBLISHABLE_KEY}")
            
            if stripe_configured:
                print("✅ Stripe configured, creating customer and subscription")
                try:
                    print("🔑 Setting Stripe API key...")
                    stripe.api_key = stripe_secret_from_env
                    print(f"🔑 Stripe API key set to: {stripe.api_key[:20]}...")
                    
                    print("👤 Creating Stripe customer...")
                    stripe_customer = stripe.Customer.create(
                        email=email,
                        metadata={'user_id': user.id}
                    )
                    print(f"✅ Stripe customer created: {stripe_customer.id}")
                    
                    plan_info = PRICING_PLANS.get(pricing_plan, PRICING_PLANS['basic'])
                    print(f"📋 Using plan info: {plan_info}")
                    
                    # Check if we already have a price for this plan in the database
                    pricing_plan_obj, created = PricingPlan.objects.get_or_create(
                        name=pricing_plan,
                        defaults={
                            'amount': plan_info['amount'],
                            'currency': 'usd',
                            'interval': 'month',
                            'stripe_price_id': ''  # Will be set below
                        }
                    )
                    
                    if created or not pricing_plan_obj.stripe_price_id:
                        # Create a new price object in Stripe
                        print(f"💰 Creating new Stripe price for {pricing_plan}...")
                        stripe_price = stripe.Price.create(
                            unit_amount=plan_info['amount'],  # Amount in cents
                            currency='usd',
                            recurring={'interval': 'month'},
                            product_data={'name': f'{pricing_plan.title()} Plan'}
                        )
                        print(f"✅ Stripe price created: {stripe_price.id}")
                        
                        # Save the Stripe price ID to our database
                        pricing_plan_obj.stripe_price_id = stripe_price.id
                        pricing_plan_obj.save()
                        print("💾 Price ID saved to database")
                    else:
                        print(f"♻️ Reusing existing Stripe price: {pricing_plan_obj.stripe_price_id}")
                        stripe_price = {'id': pricing_plan_obj.stripe_price_id}
                    
                    print("💳 Creating Stripe subscription...")
                    stripe_subscription = stripe.Subscription.create(
                        customer=stripe_customer.id,
                        items=[{'price': stripe_price.id}],
                        trial_period_days=7,
                        metadata={
                            'user_id': user.id,
                            'plan': pricing_plan
                        }
                    )
                    print(f"✅ Stripe subscription created: {stripe_subscription.id}")
                    
                    print("💾 Creating user profile...")
                    user_profile = UserProfile.objects.create(
                        user=user,
                        stripe_customer_id=stripe_customer.id,
                        stripe_subscription_id=stripe_subscription.id,
                        stripe_price_id=stripe_price['id'],
                        pricing_plan=pricing_plan,
                        subscription_status='trialing'
                    )
                    print("✅ User profile created successfully")
                    
                except stripe.error.StripeError as stripe_err:
                    print(f"❌ Stripe error: {stripe_err}")
                    print(f"❌ Stripe error type: {type(stripe_err)}")
                    print(f"❌ Stripe error details: {stripe_err.user_message if hasattr(stripe_err, 'user_message') else 'No user message'}")
                    if user:
                        user.delete()
                    return Response({
                        'error': f'Stripe error: {str(stripe_err)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as general_err:
                    print(f"❌ General error in Stripe section: {general_err}")
                    print(f"❌ Error type: {type(general_err)}")
                    import traceback
                    print(f"❌ Traceback: {traceback.format_exc()}")
                    if user:
                        user.delete()
                    return Response({
                        'error': f'Stripe setup error: {str(general_err)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                print("⚠️ Stripe not configured, creating user without subscription")
                # Create user profile without Stripe for development
                user_profile = UserProfile.objects.create(
                    user=user,
                    stripe_customer_id='dev_customer_' + str(user.id),
                    stripe_subscription_id='dev_subscription_' + str(user.id),
                    subscription_status='trialing'
                )
            
            login(request, user)
            
            return Response({
                'message': 'User created successfully',
                'user': UserProfileSerializer(user_profile).data
            }, status=status.HTTP_201_CREATED)
            
        except stripe.error.StripeError as e:
            if user:
                user.delete()
            return Response({
                'error': f'Stripe error: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if user:
                user.delete()
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        try:
            user_profile = UserProfile.objects.get(user=user)
            return Response({
                'message': 'Login successful',
                'user': UserProfileSerializer(user_profile).data
            }, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({
                'message': 'Login successful',
                'user': {'email': user.email, 'subscription_status': 'none'}
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def user_logout(request):
    print(f"🔄 Logout request received. User: {request.user}, Authenticated: {request.user.is_authenticated}")
    
    if request.user.is_authenticated:
        print("✅ User authenticated, proceeding with logout")
        # Flush the session completely
        request.session.flush()
        logout(request)
        print("🗑️ Session flushed and user logged out")
    else:
        print("⚠️ User not authenticated")
    
    # Create response and clear session cookie
    response = Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    response.delete_cookie('sessionid', domain=None, path='/')
    response.delete_cookie('csrftoken', domain=None, path='/')
    
    print("📤 Logout response sent")
    return response


@api_view(['GET'])
def check_auth(request):
    print(f"🔍 Auth check request. User: {request.user}, Authenticated: {request.user.is_authenticated}")
    
    if request.user.is_authenticated:
        print("✅ User is authenticated")
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            print("📊 User profile found")
            return Response({
                'authenticated': True,
                'user': UserProfileSerializer(user_profile).data
            }, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            print("⚠️ User profile not found, using basic data")
            return Response({
                'authenticated': True,
                'user': {'email': request.user.email, 'subscription_status': 'none'}
            }, status=status.HTTP_200_OK)
    else:
        print("❌ User is not authenticated")
        return Response({'authenticated': False}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_pricing_plans(request):
    plans = [
        {
            'id': 'basic',
            'name': 'Basic Plan',
            'price': '$9.99/month',
            'features': ['5 Users', 'Basic Analytics', 'Email Support']
        },
        {
            'id': 'pro',
            'name': 'Pro Plan',
            'price': '$19.99/month',
            'features': ['25 Users', 'Advanced Analytics', 'Priority Support', 'API Access']
        },
        {
            'id': 'enterprise',
            'name': 'Enterprise Plan',
            'price': '$49.99/month',
            'features': ['Unlimited Users', 'Custom Analytics', '24/7 Support', 'Custom Integrations']
        }
    ]
    return Response({'plans': plans}, status=status.HTTP_200_OK) 