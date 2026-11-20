from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Hotel
from app.schemas import HotelSearchResponse, HotelResponse

router = APIRouter(prefix="/api/v1/hotels", tags=["Hotel Search"])


@router.get("/search", response_model=HotelSearchResponse)
def search_hotels(
    city: str = Query(..., min_length=2, description="City name, e.g. Los Angeles, New York"),
    checkin_date: str = Query(..., description="Check-in date in YYYY-MM-DD format"),
    checkout_date: str = Query(..., description="Check-out date in YYYY-MM-DD format"),
    guests: int = Query(1, ge=1, le=10, description="Number of guests (1-10)"),
    db: Session = Depends(get_db)
):
    """
    Search available hotels by city and dates.
    Validates city location, past check-in dates, and that check-out is strictly after check-in.
    """
    city_clean = city.strip()
    if not city_clean or city_clean.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid city location provided"
        )

    # 1. Parse check-in date
    try:
        checkin_obj = datetime.strptime(checkin_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid checkin_date format. Expected YYYY-MM-DD"
        )

    today = date.today()
    if checkin_obj < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in date cannot be in the past"
        )

    # 2. Parse check-out date
    try:
        checkout_obj = datetime.strptime(checkout_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid checkout_date format. Expected YYYY-MM-DD"
        )

    # 3. Check-out must be after check-in
    if checkout_obj <= checkin_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date"
        )

    # 4. Query Hotels
    hotels = db.query(Hotel).filter(
        Hotel.city.ilike(f"%{city_clean}%"),
        Hotel.available_rooms >= 1
    ).all()

    return HotelSearchResponse(
        total_hotels=len(hotels),
        hotels=hotels
    )


@router.get("/{hotel_id}", response_model=HotelResponse)
def get_hotel_details(hotel_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single hotel by ID."""
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with ID {hotel_id} not found"
        )
    return hotel
