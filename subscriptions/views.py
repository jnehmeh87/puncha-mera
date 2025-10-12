import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Subscription, SubscriptionPlan

stripe.api_key = settings.STRIPE_API_KEY

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        price_id = request.POST.get('price_id')
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=settings.FRONTEND_URL + '/success',
                cancel_url=settings.FRONTEND_URL + '/cancel',
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            return JsonResponse({'status': 'invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return JsonResponse({'status': 'invalid signature'}, status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Fulfill the purchase...
            # Find your user in your database
            # and mark the subscription as active
            try:
                subscription = Subscription.objects.get(stripe_subscription_id=session.subscription)
                subscription.status = 'active'
                subscription.save()
            except Subscription.DoesNotExist:
                # Create a new subscription
                # This requires more information from the session, like the customer and plan
                pass

        return JsonResponse({'status': 'success'})