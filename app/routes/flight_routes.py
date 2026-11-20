from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Flight
from app.schemas import FlightSearchResponse, FlightResponse

router = APIRouter(prefix="/api/v1/flights", tags=["Flight Search"])


@router.get("/search", response_model=FlightSearchResponse)
def search_flights(
    origin: str = Query(..., description="Origin 3-letter IATA code, e.g. JFK"),
    destination: str = Query(..., description="Destination 3-letter IATA code, e.g. LAX"),
    departure_date: str = Query(..., description="Departure date in YYYY-MM-DD format"),
    return_date: Optional[str] = Query(None, description="Optional return date in YYYY-MM-DD format"),
    passengers: int = Query(1, ge=1, le=10, description="Number of passengers (1-10)"),
    db: Session = Depends(get_db)
):
    """
    Search available flights by route and dates.
    Validates origin, destination, past dates, and return date order.
    """
    # 1. Validate Origin & Destination format (3 letters)
    origin_clean = origin.strip().upper()
    dest_clean = destination.strip().upper()
    if len(origin_clean) != 3 or not origin_clean.isalpha():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid origin code. Must be a 3-letter airport code (e.g., JFK)"
        )
    if len(dest_clean) != 3 or not dest_clean.isalpha():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid destination code. Must be a 3-letter airport code (e.g., LAX)"
        )
    if origin_clean == dest_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Origin and destination cannot be the same"
        )

    # 2. Validate Departure Date format & past date check
    try:
        dep_date_obj = datetime.strptime(departure_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid departure_date format. Expected YYYY-MM-DD"
        )

    today = date.today()
    if dep_date_obj < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Departure date cannot be in the past"
        )

    # 3. Validate Return Date if provided
    if return_date:
        try:
            ret_date_obj = datetime.strptime(return_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid return_date format. Expected YYYY-MM-DD"
            )
        if ret_date_obj < dep_date_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return date cannot be earlier than departure date"
            )

    # 4. Query Database
    query = db.query(Flight).filter(
        Flight.origin == origin_clean,
        Flight.destination == dest_clean,
        Flight.available_seats >= passengers
    )

    flights = query.all()
    return FlightSearchResponse(
        total_flights=len(flights),
        flights=flights
    )


@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight_details(flight_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single flight by ID."""
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {flight_id} not found"
        )
    return flight
