from django.urls import path
from .views import CreateCheckoutSessionView, StripeWebhookView

app_name = 'subscriptions'

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]