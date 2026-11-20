from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ---------------------- AUTH SCHEMAS ----------------------
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str
    role: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=4)
    role: Optional[str] = "customer"


# ---------------------- FLIGHT SCHEMAS ----------------------
class FlightResponse(BaseModel):
    id: int
    flight_number: str
    airline: str
    origin: str
    destination: str
    departure_date: str
    departure_time: str
    arrival_time: str
    price: float
    available_seats: int

    class Config:
        from_attributes = True


class FlightSearchResponse(BaseModel):
    total_flights: int
    flights: List[FlightResponse]


# ---------------------- HOTEL SCHEMAS ----------------------
class HotelResponse(BaseModel):
    id: int
    name: str
    city: str
    address: str
    rating: float
    price_per_night: float
    available_rooms: int

    class Config:
        from_attributes = True


class HotelSearchResponse(BaseModel):
    total_hotels: int
    hotels: List[HotelResponse]


# ---------------------- BOOKING SCHEMAS ----------------------
class BookingCreateRequest(BaseModel):
    booking_type: str = Field(..., description="FLIGHT or HOTEL")
    item_id: int = Field(..., gt=0, description="Flight ID or Hotel ID")
    passengers_or_guests: int = Field(1, ge=1, le=10)
    client_reference_id: Optional[str] = Field(None, description="Client idempotency key")

    @field_validator("booking_type")
    @classmethod
    def validate_type(cls, v):
        v_upper = v.upper()
        if v_upper not in ["FLIGHT", "HOTEL"]:
            raise ValueError("booking_type must be either 'FLIGHT' or 'HOTEL'")
        return v_upper


class BookingResponse(BaseModel):
    id: int
    booking_reference: str
    user_id: int
    booking_type: str
    item_id: int
    passengers_or_guests: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingStatusResponse(BaseModel):
    booking_id: int
    booking_reference: str
    status: str
    booking_type: str
    total_price: float
    payment_status: Optional[str] = None
    cancellation_status: Optional[str] = None


# ---------------------- PAYMENT SCHEMAS ----------------------
class PaymentRequest(BaseModel):
    booking_id: int = Field(..., gt=0)
    amount: float = Field(..., description="Payment amount")
    currency: Optional[str] = Field("USD", min_length=3, max_length=3)
    payment_method: str = Field("credit_card", description="credit_card, debit_card, upi")
    card_number: Optional[str] = Field(None, description="Simulate card numbers for testing")


class PaymentResponse(BaseModel):
    payment_id: int
    payment_reference: str
    booking_id: int
    amount: float
    currency: str
    payment_method: str
    status: str
    transaction_date: datetime
    failure_reason: Optional[str] = None

    class Config:
        from_attributes = True


# ---------------------- CANCELLATION SCHEMAS ----------------------
class CancellationRequest(BaseModel):
    reason: str = Field("Change of plans", min_length=3, max_length=255)


class CancellationResponse(BaseModel):
    cancellation_id: int
    booking_id: int
    cancellation_reason: str
    refund_amount: float
    refund_status: str
    cancelled_at: datetime
    booking_status: str
