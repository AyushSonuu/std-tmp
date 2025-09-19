from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_active_user, AutoPermission
from app.core.permissions import AppPermissions
from app.db.session import get_db
from app.models.user import User
from app.services.payment.service import PaymentService
from app.services.payment.schemas import PaymentRead, PaymentCreate, PaymentVerify, PaymentRefund

router = APIRouter()

@router.post(
    "/",
    response_model=PaymentRead,
    dependencies=[Depends(AutoPermission(override=AppPermissions.PAYMENTS_CREATE))],
    status_code=status.HTTP_201_CREATED,
)
async def create_new_payment(
    payment_in: PaymentCreate,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new payment."""
    payment_service = PaymentService(db)
    payment_data = await payment_service.create_payment(
        user_id=current_user.id,
        amount=payment_in.amount,
        currency=payment_in.currency,
        metadata=payment_in.metadata,
    )
    # The service returns a dict, but we want to return a Pydantic model
    # We need to fetch the full payment object from the DB
    full_payment = await payment_service.get_payment(payment_data["payment_id"])
    if not full_payment:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Payment not found after creation")
    return full_payment


@router.post(
    "/{payment_id}/verify",
    response_model=PaymentRead,
    dependencies=[Depends(AutoPermission(override=AppPermissions.PAYMENTS_CREATE))], # Re-using create perm for verify for simplicity
)
async def verify_existing_payment(
    payment_id: int,
    payment_verify_in: PaymentVerify,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify an existing payment. Users can only verify their own payments."""
    payment_service = PaymentService(db)
    payment = await payment_service.get_payment(payment_id)

    if not payment or payment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found or not authorized")
    
    verification_result = await payment_service.verify_payment(payment_id, payment_verify_in.model_dump())
    if not verification_result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=verification_result.get("error", "Payment verification failed"))
    
    updated_payment = await payment_service.get_payment(payment_id)
    if not updated_payment:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Payment not found after verification")
    return updated_payment


@router.get(
    "/",
    response_model=List[PaymentRead],
)
async def list_current_user_payments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all payments for the current user."""
    payment_service = PaymentService(db)
    payments = await payment_service.list_payments(user_id=current_user.id, skip=skip, limit=limit)
    return payments


@router.get(
    "/{payment_id}",
    response_model=PaymentRead,
)
async def get_payment_by_id(
    payment_id: int,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific payment by ID. Users can only view their own payments."""
    payment_service = PaymentService(db)
    payment = await payment_service.get_payment(payment_id)

    if not payment or payment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found or not authorized")
    
    return payment
