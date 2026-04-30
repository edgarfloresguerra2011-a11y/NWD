import stripe
from app.config import settings
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_API_KEY

async def create_checkout_session(user_id: int, user_email: str):
    """Create a Stripe Checkout Session for subscription."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': settings.STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='http://localhost:3000/dashboard?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:3000/billing',
            customer_email=user_email,
            metadata={
                'user_id': user_id
            }
        )
        return session.url
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        return None

def verify_webhook(payload, sig_header):
    """Verify Stripe webhook signature."""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return None
