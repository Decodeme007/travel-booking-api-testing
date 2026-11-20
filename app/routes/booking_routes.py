import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Booking, Flight, Hotel, User, Cancellation
from app.schemas import (
    BookingCreateRequest,
    BookingResponse,
    BookingStatusResponse,
    CancellationRequest,
    CancellationResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    request: BookingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new travel booking (FLIGHT or HOTEL).
    Requires authentication. Supports idempotency via client_reference_id.
    """
    # 1. Idempotency / Duplicate Booking Check
    if request.client_reference_id:
        existing = db.query(Booking).filter(
            Booking.booking_reference == request.client_reference_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate booking detected with reference '{request.client_reference_id}'"
            )

    # 2. Validate Item existence & calculate price
    total_price = 0.0
    if request.booking_type == "FLIGHT":
        flight = db.query(Flight).filter(Flight.id == request.item_id).first()
        if not flight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flight ID {request.item_id} not found"
            )
        if flight.available_seats < request.passengers_or_guests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough available seats for this flight"
            )
        total_price = flight.price * request.passengers_or_guests
        # Reserve seats
        flight.available_seats -= request.passengers_or_guests

    elif request.booking_type == "HOTEL":
        hotel = db.query(Hotel).filter(Hotel.id == request.item_id).first()
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hotel ID {request.item_id} not found"
            )
        if hotel.available_rooms < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available rooms in this hotel"
            )
        total_price = hotel.price_per_night * request.passengers_or_guests
        # Reserve room
        hotel.available_rooms -= 1

    # 3. Create Booking Record
    ref_code = request.client_reference_id or f"BK-{uuid.uuid4().hex[:8].upper()}"
    new_booking = Booking(
        booking_reference=ref_code,
        user_id=current_user.id,
        booking_type=request.booking_type,
        item_id=request.item_id,
        passengers_or_guests=request.passengers_or_guests,
        total_price=round(total_price, 2),
        status="PENDING"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full details of a booking by ID."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    # Check authorization (admin can view any, user can only view their own)
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are not authorized to view this booking"
        )
    return booking


@router.get("/{booking_id}/status", response_model=BookingStatusResponse)
def get_booking_status(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Booking status verification endpoint."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are not authorized to view this booking status"
        )

    payment_status = booking.payment.status if booking.payment else None
    cancellation_status = booking.cancellation.refund_status if booking.cancellation else None

    return BookingStatusResponse(
        booking_id=booking.id,
        booking_reference=booking.booking_reference,
        status=booking.status,
        booking_type=booking.booking_type,
        total_price=booking.total_price,
        payment_status=payment_status,
        cancellation_status=cancellation_status
    )


@router.post("/{booking_id}/cancel", response_model=CancellationResponse)
def cancel_booking(
    booking_id: int,
    request: CancellationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an existing booking and issue simulated refund.
    Validates double cancellation, non-existent booking, and authorization.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )

    # Authorization check
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are not authorized to cancel this booking"
        )

    # Check if already cancelled
    if booking.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled. Cannot cancel twice."
        )

    # Calculate refund: 100% if PENDING or CONFIRMED
    refund_amount = booking.total_price if booking.status == "CONFIRMED" else 0.0

    # Release inventory back
    if booking.booking_type == "FLIGHT":
        flight = db.query(Flight).filter(Flight.id == booking.item_id).first()
        if flight:
            flight.available_seats += booking.passengers_or_guests
    elif booking.booking_type == "HOTEL":
        hotel = db.query(Hotel).filter(Hotel.id == booking.item_id).first()
        if hotel:
            hotel.available_rooms += 1

    # Update booking status
    booking.status = "CANCELLED"
    booking.updated_at = datetime.utcnow()

    # Create Cancellation record
    cancellation = Cancellation(
        booking_id=booking.id,
        cancellation_reason=request.reason,
        refund_amount=refund_amount,
        refund_status="PROCESSED" if refund_amount > 0 else "N/A"
    )
    db.add(cancellation)
    db.commit()
    db.refresh(cancellation)

    return CancellationResponse(
        cancellation_id=cancellation.id,
        booking_id=booking.id,
        cancellation_reason=cancellation.cancellation_reason,
        refund_amount=cancellation.refund_amount,
        refund_status=cancellation.refund_status,
        cancelled_at=cancellation.cancelled_at,
        booking_status=booking.status
    )
