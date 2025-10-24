# Payment Model - Placeholder for Future Implementation
# TODO: Implement payment processing integration (Stripe, PayPal, etc.)

from datetime import datetime
from typing import Optional, Dict, Any
from google.cloud import firestore

class PaymentPlan:
    """Payment plan model - Placeholder"""

    def __init__(self, plan_id: str, name: str, price: float,
                 features: Dict[str, Any], billing_period: str = 'monthly'):
        self.plan_id = plan_id
        self.name = name
        self.price = price
        self.features = features
        self.billing_period = billing_period  # 'monthly', 'yearly', 'one-time'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'plan_id': self.plan_id,
            'name': self.name,
            'price': self.price,
            'features': self.features,
            'billing_period': self.billing_period
        }

class UserSubscription:
    """User subscription model - Placeholder"""

    def __init__(self, user_id: str, plan_id: str,
                 status: str = 'active', started_at: datetime = None,
                 expires_at: datetime = None):
        self.user_id = user_id
        self.plan_id = plan_id
        self.status = status  # 'active', 'cancelled', 'expired', 'trial'
        self.started_at = started_at or datetime.utcnow()
        self.expires_at = expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'status': self.status,
            'started_at': self.started_at,
            'expires_at': self.expires_at
        }

class PaymentService:
    """Payment service - Placeholder for future implementation"""

    def __init__(self):
        self.db = firestore.Client()
        self.collection = 'subscriptions'

    # TODO: Implement these methods when payment integration is ready
    def create_subscription(self, user_id: str, plan_id: str) -> bool:
        """Create a new subscription for user"""
        raise NotImplementedError("Payment processing not yet implemented")

    def cancel_subscription(self, user_id: str) -> bool:
        """Cancel user subscription"""
        raise NotImplementedError("Payment processing not yet implemented")

    def verify_payment(self, payment_id: str) -> bool:
        """Verify payment completion"""
        raise NotImplementedError("Payment processing not yet implemented")

    def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """Get user's current subscription"""
        raise NotImplementedError("Payment processing not yet implemented")

# Predefined payment plans (example)
PAYMENT_PLANS = {
    'free': PaymentPlan(
        plan_id='free',
        name='Free Plan',
        price=0.0,
        features={
            'messages_per_day': 10,
            'models': ['gpt-3.5-turbo'],
            'support': 'community'
        }
    ),
    'pro': PaymentPlan(
        plan_id='pro',
        name='Pro Plan',
        price=29.99,
        features={
            'messages_per_day': 1000,
            'models': ['gpt-3.5-turbo', 'gpt-4', 'gemini-pro'],
            'support': 'email',
            'priority_access': True
        }
    ),
    'enterprise': PaymentPlan(
        plan_id='enterprise',
        name='Enterprise Plan',
        price=299.99,
        features={
            'messages_per_day': 'unlimited',
            'models': 'all',
            'support': 'dedicated',
            'priority_access': True,
            'custom_models': True,
            'sla': True
        }
    )
}
