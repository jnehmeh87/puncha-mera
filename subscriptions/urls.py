from django.urls import path
from .views import CreateCheckoutSessionView, StripeWebhookView, PricingView

app_name = 'subscriptions'

urlpatterns = [
    path('pricing/', PricingView.as_view(), name='pricing'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('webhook/', StripeWebhookView.as_view(), name='webhook'),
]