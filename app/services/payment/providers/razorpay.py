import razorpay
from typing import Dict, Any

from .base import PaymentProvider
from app.core.config import settings

class RazorpayProvider(PaymentProvider):
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    async def create_order(self, amount: int, currency: str = "INR", **kwargs) -> Dict[str, Any]:
        order_data = {
            "amount": amount * 100,  # Razorpay expects amount in paise
            "currency": currency,
            "receipt": kwargs.get("receipt", f"order_{kwargs.get('order_id', 'unknown')}"),
            "notes": kwargs.get("notes", {})
        }
        try:
            order = self.client.order.create(order_data)
            return {
                "success": True,
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "provider_data": order
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def verify_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.client.utility.verify_payment_signature({
                "razorpay_order_id": payment_data["order_id"],
                "razorpay_payment_id": payment_data["payment_id"],
                "razorpay_signature": payment_data["signature"]
            })
            return {"success": True, "verified": True}
        except Exception as e:
            return {"success": False, "verified": False, "error": str(e)}

    async def capture_payment(self, payment_id: str, amount: int) -> Dict[str, Any]:
        try:
            result = self.client.payment.capture(payment_id, amount * 100)
            return {"success": True, "captured": True, "provider_data": result}
        except Exception as e:
            return {"success": False, "captured": False, "error": str(e)}

    async def refund_payment(self, payment_id: str, amount: int) -> Dict[str, Any]:
        try:
            refund_data = {"amount": amount * 100, "notes": {"reason": "requested_by_customer"}}
            result = self.client.payment.refund(payment_id, refund_data)
            return {"success": True, "refund_id": result["id"], "provider_data": result}
        except Exception as e:
            return {"success": False, "error": str(e)} 