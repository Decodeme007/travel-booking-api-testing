import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="customer")  # customer, admin
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")


class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    flight_number = Column(String(20), unique=True, index=True, nullable=False)
    airline = Column(String(100), nullable=False)
    origin = Column(String(10), index=True, nullable=False)  # Airport code e.g. JFK, LAX
    destination = Column(String(10), index=True, nullable=False)
    departure_date = Column(String(10), index=True, nullable=False)  # YYYY-MM-DD
    departure_time = Column(String(20), nullable=False)
    arrival_time = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    available_seats = Column(Integer, default=50, nullable=False)


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    city = Column(String(50), index=True, nullable=False)
    address = Column(String(255), nullable=False)
    rating = Column(Float, default=4.0)
    price_per_night = Column(Float, nullable=False)
    available_rooms = Column(Integer, default=20, nullable=False)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_reference = Column(String(30), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_type = Column(String(20), nullable=False)  # FLIGHT or HOTEL
    item_id = Column(Integer, nullable=False)  # Flight ID or Hotel ID
    passengers_or_guests = Column(Integer, default=1, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)  # PENDING, CONFIRMED, CANCELLED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    cancellation = relationship("Cancellation", back_populates="booking", uselist=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_reference = Column(String(40), unique=True, index=True, nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(5), default="USD", nullable=False)
    payment_method = Column(String(30), nullable=False)  # credit_card, debit_card, upi, etc.
    status = Column(String(20), nullable=False)  # SUCCESS, FAILED
    transaction_date = Column(DateTime, default=datetime.datetime.utcnow)
    failure_reason = Column(String(255), nullable=True)

    booking = relationship("Booking", back_populates="payment")


class Cancellation(Base):
    __tablename__ = "cancellations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    cancellation_reason = Column(String(255), nullable=False)
    refund_amount = Column(Float, nullable=False)
    refund_status = Column(String(20), default="PROCESSED", nullable=False)  # PROCESSED, PENDING
    cancelled_at = Column(DateTime, default=datetime.datetime.utcnow)

    booking = relationship("Booking", back_populates="cancellation")
