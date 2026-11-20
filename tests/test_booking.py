import pytest
from framework.api_clients.booking_client import BookingClient
from framework.database.db_helper import DatabaseHelper
from framework.schemas.booking_schema import BOOKING_RESPONSE_SCHEMA
from framework.utils.assertions import assert_status_code, assert_json_schema, assert_response_time
from framework.utils.data_generator import generate_random_string


class TestBookingAPI:
    """SDET Test Suite for Booking Creation and Database Consistency."""

    def test_create_flight_booking_success_and_db_consistency(
        self,
        booking_client: BookingClient,
        db_helper: DatabaseHelper
    ):
        """TC-BOOKING-01: Verify flight booking creation (201 Created) and database seat deduction."""
        flight_id = 1
        initial_seats = db_helper.get_flight_seats(flight_id)
        passengers = 2
        ref_id = f"TEST-BK-{generate_random_string(6).upper()}"

        response = booking_client.create_booking(
            booking_type="FLIGHT",
            item_id=flight_id,
            passengers_or_guests=passengers,
            client_reference_id=ref_id
        )
        assert_status_code(response, 201)
        assert_response_time(response)
        assert_json_schema(response, BOOKING_RESPONSE_SCHEMA)

        data = response.json()
        booking_id = data["id"]
        assert data["booking_reference"] == ref_id
        assert data["status"] == "PENDING"
        assert data["passengers_or_guests"] == passengers

        # Database Consistency Testing: SQL Queries
        db_record = db_helper.get_booking_by_id(booking_id)
        assert db_record is not None, "Booking record was not found in SQL database!"
        assert db_record["booking_reference"] == ref_id
        assert db_record["status"] == "PENDING"
        assert db_record["total_price"] == data["total_price"]

        updated_seats = db_helper.get_flight_seats(flight_id)
        assert updated_seats == initial_seats - passengers, (
            f"Expected available seats to decrease by {passengers}. Initial: {initial_seats}, Now: {updated_seats}"
        )

    def test_create_hotel_booking_success(self, booking_client: BookingClient, db_helper: DatabaseHelper):
        """TC-BOOKING-02: Verify hotel booking creation (201 Created) and SQL database persistence."""
        hotel_id = 1
        ref_id = f"TEST-HTL-{generate_random_string(6).upper()}"

        response = booking_client.create_booking(
            booking_type="HOTEL",
            item_id=hotel_id,
            passengers_or_guests=1,
            client_reference_id=ref_id
        )
        assert_status_code(response, 201)
        assert_json_schema(response, BOOKING_RESPONSE_SCHEMA)

        booking_id = response.json()["id"]
        db_record = db_helper.get_booking_by_id(booking_id)
        assert db_record is not None
        assert db_record["booking_type"] == "HOTEL"

    def test_duplicate_booking_conflict(self, booking_client: BookingClient):
        """TC-BOOKING-03: Verify duplicate booking creation with identical reference returns 409 Conflict."""
        duplicate_ref = f"DUP-{generate_random_string(6).upper()}"

        # First request succeeds
        res1 = booking_client.create_booking(
            booking_type="FLIGHT",
            item_id=2,
            passengers_or_guests=1,
            client_reference_id=duplicate_ref
        )
        assert_status_code(res1, 201)

        # Second request with duplicate reference fails
        res2 = booking_client.create_booking(
            booking_type="FLIGHT",
            item_id=2,
            passengers_or_guests=1,
            client_reference_id=duplicate_ref
        )
        assert_status_code(res2, 409)
        assert "Duplicate booking detected" in res2.json()["detail"]

    def test_booking_nonexistent_flight(self, booking_client: BookingClient):
        """TC-BOOKING-04: Verify booking a non-existent flight returns 404 Not Found."""
        response = booking_client.create_booking(
            booking_type="FLIGHT",
            item_id=99999,
            passengers_or_guests=1
        )
        assert_status_code(response, 404)
        assert "not found" in response.json()["detail"].lower()

    def test_booking_invalid_booking_type(self, booking_client: BookingClient):
        """TC-BOOKING-05: Verify unsupported booking_type returns 422 Unprocessable Entity."""
        response = booking_client.create_booking(
            booking_type="CRUISE",
            item_id=1,
            passengers_or_guests=1
        )
        assert_status_code(response, 422)

    def test_booking_unauthorized_access(self):
        """TC-BOOKING-06: Verify unauthenticated user cannot create a booking (401 Unauthorized)."""
        unauth_client = BookingClient()
        response = unauth_client.create_booking(
            booking_type="FLIGHT",
            item_id=1,
            passengers_or_guests=1
        )
        assert_status_code(response, 401)
