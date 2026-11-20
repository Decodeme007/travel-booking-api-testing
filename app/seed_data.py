from datetime import datetime, timedelta
from app.database import SessionLocal, Base, engine
from app.models import User, Flight, Hotel
from app.auth import hash_password


def seed_database():
    """Populate realistic test seed data for Flights, Hotels, and Users."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Users if not present
        if db.query(User).count() == 0:
            test_users = [
                User(
                    username="testuser",
                    email="testuser@traveltest.com",
                    password_hash=hash_password("Password123!"),
                    role="customer"
                ),
                User(
                    username="adminuser",
                    email="admin@traveltest.com",
                    password_hash=hash_password("AdminSecure2026!"),
                    role="admin"
                ),
                User(
                    username="traveler_jane",
                    email="jane@traveltest.com",
                    password_hash=hash_password("JaneSecret456!"),
                    role="customer"
                )
            ]
            db.add_all(test_users)
            db.commit()

        # 2. Seed Flights (dynamic dates starting from tomorrow to ensure searches are valid)
        if db.query(Flight).count() == 0:
            base_date = datetime.utcnow().date()
            flights = [
                Flight(
                    flight_number="AA-101",
                    airline="American Airlines",
                    origin="JFK",
                    destination="LAX",
                    departure_date=(base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                    departure_time="08:30 AM",
                    arrival_time="11:45 AM",
                    price=299.50,
                    available_seats=45
                ),
                Flight(
                    flight_number="DL-202",
                    airline="Delta Air Lines",
                    origin="JFK",
                    destination="LAX",
                    departure_date=(base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                    departure_time="01:15 PM",
                    arrival_time="04:30 PM",
                    price=325.00,
                    available_seats=30
                ),
                Flight(
                    flight_number="UA-303",
                    airline="United Airlines",
                    origin="SFO",
                    destination="ORD",
                    departure_date=(base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                    departure_time="09:00 AM",
                    arrival_time="03:15 PM",
                    price=210.00,
                    available_seats=15
                ),
                Flight(
                    flight_number="BA-404",
                    airline="British Airways",
                    origin="LHR",
                    destination="JFK",
                    departure_date=(base_date + timedelta(days=10)).strftime("%Y-%m-%d"),
                    departure_time="10:30 AM",
                    arrival_time="01:45 PM",
                    price=580.00,
                    available_seats=20
                ),
                Flight(
                    flight_number="EK-505",
                    airline="Emirates",
                    origin="DXB",
                    destination="LHR",
                    departure_date=(base_date + timedelta(days=12)).strftime("%Y-%m-%d"),
                    departure_time="02:20 AM",
                    arrival_time="06:45 AM",
                    price=620.00,
                    available_seats=5
                ),
                Flight(
                    flight_number="SW-606",
                    airline="Southwest Airlines",
                    origin="JFK",
                    destination="LAX",
                    departure_date=(base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                    departure_time="06:00 PM",
                    arrival_time="09:20 PM",
                    price=180.00,
                    available_seats=12
                )
            ]
            db.add_all(flights)
            db.commit()

        # 3. Seed Hotels
        if db.query(Hotel).count() == 0:
            hotels = [
                Hotel(
                    name="Grand Plaza Hotel",
                    city="Los Angeles",
                    address="100 Grand Ave, Los Angeles, CA",
                    rating=4.5,
                    price_per_night=180.00,
                    available_rooms=25
                ),
                Hotel(
                    name="Sunset Boulevard Resort",
                    city="Los Angeles",
                    address="8440 Sunset Blvd, West Hollywood, CA",
                    rating=4.8,
                    price_per_night=250.00,
                    available_rooms=10
                ),
                Hotel(
                    name="Midtown Luxury Suites",
                    city="New York",
                    address="350 5th Ave, New York, NY",
                    rating=4.7,
                    price_per_night=310.00,
                    available_rooms=15
                ),
                Hotel(
                    name="Central Park View Hotel",
                    city="New York",
                    address="59 Central Park S, New York, NY",
                    rating=4.9,
                    price_per_night=420.00,
                    available_rooms=8
                ),
                Hotel(
                    name="Thames Riverside Inn",
                    city="London",
                    address="20 River Walk, London, UK",
                    rating=4.3,
                    price_per_night=195.00,
                    available_rooms=18
                ),
                Hotel(
                    name="Paris Eiffel Boutique",
                    city="Paris",
                    address="12 Rue de Champ de Mars, Paris, France",
                    rating=4.6,
                    price_per_night=220.00,
                    available_rooms=14
                )
            ]
            db.add_all(hotels)
            db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
    print("Database schema created and seed data populated successfully.")
