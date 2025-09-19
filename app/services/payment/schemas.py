from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

class PaymentBase(BaseModel):
    amount: float
    currency: str = "INR"
    metadata: Optional[Dict[str, Any]] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentRead(PaymentBase):
    id: int
    user_id: int
    status: str
    provider: str
    provider_order_id: Optional[str] = None
    provider_payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    provider_payment_id: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None

class PaymentVerify(BaseModel):
    payment_id: str
    order_id: str
    signature: str

class PaymentRefund(BaseModel):
    amount: float
    reason: Optional[str] = None 