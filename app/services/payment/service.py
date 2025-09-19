from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.services.payment.models import Payment
from app.services.payment.providers.razorpay import RazorpayProvider
# from app.services.payment.providers.stripe import StripeProvider # Future provider

class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.providers = {
            "razorpay": RazorpayProvider(),
            # "stripe": StripeProvider(),  # Add when needed
        }
        self.default_provider = settings.DEFAULT_PAYMENT_PROVIDER or "razorpay"

    async def create_payment(
        self, user_id: int, amount: float, currency: str = "INR",
        provider: str = None, metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        provider_name = provider or self.default_provider
        payment_provider = self.providers.get(provider_name)
        if not payment_provider:
            raise ValueError(f"Provider {provider_name} not supported")

        order_data = await payment_provider.create_order(
            amount=int(amount),
            currency=currency,
            order_id=f"order_{user_id}_{datetime.utcnow().timestamp()}",
            notes=metadata or {}
        )
        if not order_data.get("success"):
            raise Exception(f"Failed to create order: {order_data.get('error')}")

        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            provider=provider_name,
            provider_order_id=order_data["order_id"],
            provider_data=order_data["provider_data"],
            metadata=metadata,
            status="pending"
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)

        return {
            "payment_id": payment.id,
            "order_id": order_data["order_id"],
            "amount": amount,
            "currency": currency,
            "provider": provider_name,
            "provider_data": order_data["provider_data"]
        }

    async def verify_payment(self, payment_id: int, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        payment = await self.get_payment(payment_id)
        if not payment:
            return {"success": False, "error": "Payment not found"}

        provider = self.providers.get(payment.provider)
        if not provider:
            return {"success": False, "error": "Provider not found"}

        try:
            verification_result = await provider.verify_payment(payment_data)
            if verification_result.get("success") and verification_result.get("verified"):
                await self.update_payment(payment_id, {
                    "status": "completed",
                    "provider_payment_id": payment_data["payment_id"],
                    "provider_data": {**payment.provider_data, **payment_data} if payment.provider_data else payment_data
                })
                return {"success": True, "status": "completed", "payment_id": payment_id}
            else:
                await self.update_payment(payment_id, {"status": "failed"})
                return {"success": False, "status": "failed", "error": verification_result.get("error")}
        except Exception as e:
            await self.update_payment(payment_id, {"status": "failed"})
            return {"success": False, "status": "failed", "error": str(e)}

    async def refund_payment(self, payment_id: int, amount: float, reason: str = None) -> Dict[str, Any]:
        payment = await self.get_payment(payment_id)
        if not payment:
            return {"success": False, "error": "Payment not found"}
        if payment.status != "completed":
            return {"success": False, "error": "Payment not completed"}

        provider = self.providers.get(payment.provider)
        if not provider:
            return {"success": False, "error": "Provider not found"}

        try:
            refund_result = await provider.refund_payment(payment.provider_payment_id, int(amount))
            if refund_result.get("success"):
                await self.update_payment(payment_id, {"status": "refunded"})
                return {"success": True, "refund_id": refund_result.get("refund_id")}
            else:
                return {"success": False, "error": refund_result.get("error")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_payment(self, payment_id: int) -> Optional[Payment]:
        return await self.db.get(Payment, payment_id)

    async def list_payments(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[Payment]:
        query = select(Payment)
        if user_id:
            query = query.filter(Payment.user_id == user_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_payment(self, payment_id: int, data: Dict[str, Any]) -> Payment:
        payment = await self.get_payment(payment_id)
        if payment:
            for key, value in data.items():
                setattr(payment, key, value)
            payment.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(payment)
        return payment 