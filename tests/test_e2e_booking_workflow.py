import pytest
from framework.api_clients.flight_client import FlightClient
from framework.api_clients.booking_client import BookingClient
from framework.api_clients.payment_client import PaymentClient
from framework.database.db_helper import DatabaseHelper
from framework.utils.assertions import assert_status_code, assert_json_schema, assert_response_time
from framework.utils.data_generator import generate_future_date, generate_random_string
from framework.schemas.booking_schema import BOOKING_RESPONSE_SCHEMA, CANCELLATION_RESPONSE_SCHEMA
from framework.schemas.payment_schema import PAYMENT_SUCCESS_SCHEMA


class TestE2EBookingWorkflow:
    """End-to-End Regression Flow: Search -> Book -> Pay -> Verify Status -> Cancel -> DB Check."""

    def test_e2e_flight_lifecycle(
        self,
        flight_client: FlightClient,
        booking_client: BookingClient,
        payment_client: PaymentClient,
        db_helper: DatabaseHelper
    ):
        """
        Comprehensive SDET E2E Test:
        Step 1: Search flights from JFK to LAX.
        Step 2: Select first flight.
        Step 3: Book flight for 2 passengers.
        Step 4: Verify SQL DB holds PENDING booking & reduced seat count.
        Step 5: Process payment for exact booking total.
        Step 6: Verify payment response & booking transition to CONFIRMED.
        Step 7: Verify SQL DB payment row & confirmed booking status.
        Step 8: Cancel booking.
        Step 9: Verify refund & booking transition to CANCELLED.
        Step 10: Verify SQL DB inventory seats restored to original count.
        """
        # --- STEP 1: Search Flights ---
        dep_date = generate_future_date(5)
        search_res = flight_client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=dep_date,
            passengers=2
        )
        assert_status_code(search_res, 200)
        flights = search_res.json()["flights"]
        assert len(flights) > 0, "No flights available for test route!"

        # --- STEP 2: Select Flight ---
        selected_flight = flights[0]
        flight_id = selected_flight["id"]
        passengers = 2
        initial_seats = db_helper.get_flight_seats(flight_id)

        # --- STEP 3: Create Booking ---
        ref_id = f"E2E-BK-{generate_random_string(6).upper()}"
        book_res = booking_client.create_booking(
            booking_type="FLIGHT",
            item_id=flight_id,
            passengers_or_guests=passengers,
            client_reference_id=ref_id
        )
        assert_status_code(book_res, 201)
        assert_json_schema(book_res, BOOKING_RESPONSE_SCHEMA)
        booking_data = book_res.json()
        booking_id = booking_data["id"]
        total_price = booking_data["total_price"]
        assert booking_data["status"] == "PENDING"

        # --- STEP 4: Database Consistency Check (PENDING) ---
        db_booking = db_helper.get_booking_by_id(booking_id)
        assert db_booking is not None
        assert db_booking["status"] == "PENDING"
        seats_after_booking = db_helper.get_flight_seats(flight_id)
        assert seats_after_booking == initial_seats - passengers

        # --- STEP 5: Process Payment ---
        pay_res = payment_client.process_payment(
            booking_id=booking_id,
            amount=total_price,
            payment_method="credit_card",
            currency="USD"
        )
        assert_status_code(pay_res, 200)
        assert_json_schema(pay_res, PAYMENT_SUCCESS_SCHEMA)
        payment_data = pay_res.json()
        assert payment_data["status"] == "SUCCESS"

        # --- STEP 6: Status Verification (CONFIRMED) ---
        status_res = booking_client.get_booking_status(booking_id)
        assert_status_code(status_res, 200)
        assert status_res.json()["status"] == "CONFIRMED"
        assert status_res.json()["payment_status"] == "SUCCESS"

        # --- STEP 7: Database Consistency Check (CONFIRMED) ---
        db_payment = db_helper.get_payment_for_booking(booking_id)
        assert db_payment is not None
        assert db_payment["status"] == "SUCCESS"
        db_booking_confirmed = db_helper.get_booking_by_id(booking_id)
        assert db_booking_confirmed is not None
        assert db_booking_confirmed["status"] == "CONFIRMED"

        # --- STEP 8: Cancel Booking ---
        cancel_res = booking_client.cancel_booking(
            booking_id=booking_id,
            reason="E2E test cancellation workflow"
        )
        assert_status_code(cancel_res, 200)
        assert_json_schema(cancel_res, CANCELLATION_RESPONSE_SCHEMA)
        assert cancel_res.json()["booking_status"] == "CANCELLED"
        assert cancel_res.json()["refund_amount"] == total_price

        # --- STEP 9: Status Verification (CANCELLED) ---
        status_res_after_cancel = booking_client.get_booking_status(booking_id)
        assert status_res_after_cancel.json()["status"] == "CANCELLED"
        assert status_res_after_cancel.json()["cancellation_status"] == "PROCESSED"

        # --- STEP 10: Database Consistency Check (Restored Inventory) ---
        final_seats = db_helper.get_flight_seats(flight_id)
        assert final_seats == initial_seats, (
            f"Expected available seats to be restored to {initial_seats}, but found {final_seats}"
        )
        db_cancellation = db_helper.get_cancellation_for_booking(booking_id)
        assert db_cancellation is not None
        assert db_cancellation["refund_status"] == "PROCESSED"
