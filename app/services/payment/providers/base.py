from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentProvider(ABC):
    """Base class for all payment providers"""

    @abstractmethod
    async def create_order(self, amount: int, currency: str, **kwargs) -> Dict[str, Any]:
        """Create a payment order"""
        pass

    @abstractmethod
    async def verify_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify payment"""
        pass

    @abstractmethod
    async def capture_payment(self, payment_id: str, amount: int) -> Dict[str, Any]:
        """Capture payment"""
        pass

    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: int) -> Dict[str, Any]:
        """Refund payment"""
        pass 