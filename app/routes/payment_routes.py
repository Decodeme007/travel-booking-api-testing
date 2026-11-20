import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Payment, Booking, User
from app.schemas import PaymentRequest, PaymentResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/payments", tags=["Payment Simulation"])

# Known simulation trigger values for testing
FAILED_CARD_NUMBER = "4000000000000002"
DECLINED_REASON = "Card declined: Insufficient funds or invalid CVV"


@router.post("/process", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
def process_payment(
    request: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process and simulate payment for an active booking.
    Validates amount correctness, booking state, card simulation flags, and updates booking status to CONFIRMED.
    """
    # 1. Fetch booking
    booking = db.query(Booking).filter(Booking.id == request.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking ID {request.booking_id} not found"
        )

    # 2. Authorization check
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot pay for another user's booking"
        )

    # 3. Check if booking is in valid state for payment
    if booking.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot process payment for a cancelled booking"
        )
    if booking.status == "CONFIRMED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already paid and confirmed"
        )

    # 4. Validate Amount
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than zero"
        )
    # Check if amount matches total_price
    if round(request.amount, 2) != round(booking.total_price, 2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ({request.amount}) does not match booking total ({booking.total_price})"
        )

    # 5. Simulate Payment Failure Scenario
    is_failed = False
    fail_reason = None
    if request.card_number == FAILED_CARD_NUMBER:
        is_failed = True
        fail_reason = DECLINED_REASON

    payment_ref = f"PAY-{uuid.uuid4().hex[:10].upper()}"
    payment_status = "FAILED" if is_failed else "SUCCESS"

    payment = Payment(
        payment_reference=payment_ref,
        booking_id=booking.id,
        amount=request.amount,
        currency=request.currency or "USD",
        payment_method=request.payment_method,
        status=payment_status,
        transaction_date=datetime.utcnow(),
        failure_reason=fail_reason
    )
    db.add(payment)

    if not is_failed:
        booking.status = "CONFIRMED"
        booking.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(payment)

    # If simulated failure, we return 402 Payment Required or 400 Bad Request with details
    if is_failed:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": "Payment simulation failed",
                "payment_id": payment.id,
                "payment_reference": payment.payment_reference,
                "status": "FAILED",
                "failure_reason": fail_reason
            }
        )

    return PaymentResponse(
        payment_id=payment.id,
        payment_reference=payment.payment_reference,
        booking_id=payment.booking_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment.payment_method,
        status=payment.status,
        transaction_date=payment.transaction_date,
        failure_reason=payment.failure_reason
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment_details(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve payment receipt by ID."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment ID {payment_id} not found"
        )
    return payment
