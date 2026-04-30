from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.security import get_current_user
from app.models.user import User
from app.services.stripe_service import create_checkout_session, verify_webhook
import stripe

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])

@router.post("/checkout")
async def start_checkout(current_user: User = Depends(get_current_user)):
    """Start a checkout session for the user."""
    url = await create_checkout_session(current_user.id, current_user.email)
    if not url:
        raise HTTPException(status_code=500, detail="Error al crear sesión de pago")
    return {"checkout_url": url}

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    event = verify_webhook(payload, sig_header)
    if not event:
        raise HTTPException(status_code=400, detail="Webhook inválido")
    
    # Handle event (subscription created/deleted)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        # Update user status to 'pro' or similar
        print(f"User {user_id} subscribed successfully!")
        
    return {"status": "success"}
