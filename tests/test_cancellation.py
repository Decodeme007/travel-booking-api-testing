import pytest
from framework.api_clients.booking_client import BookingClient
from framework.api_clients.payment_client import PaymentClient
from framework.database.db_helper import DatabaseHelper
from framework.schemas.booking_schema import CANCELLATION_RESPONSE_SCHEMA
from framework.utils.assertions import assert_status_code, assert_json_schema, assert_response_time


class TestCancellationAPI:
    """SDET Test Suite for Booking Cancellation & Refund Logic."""

    def test_cancel_pending_booking_success(
        self,
        booking_client: BookingClient,
        db_helper: DatabaseHelper
    ):
        """TC-CANCEL-01: Verify cancelling a PENDING booking updates status to CANCELLED and creates cancellation record."""
        create_res = booking_client.create_booking(booking_type="FLIGHT", item_id=1, passengers_or_guests=1)
        assert create_res.status_code == 201
        booking_id = create_res.json()["id"]

        cancel_res = booking_client.cancel_booking(
            booking_id=booking_id,
            reason="Customer changed schedule"
        )
        assert_status_code(cancel_res, 200)
        assert_response_time(cancel_res)
        assert_json_schema(cancel_res, CANCELLATION_RESPONSE_SCHEMA)

        cancel_data = cancel_res.json()
        assert cancel_data["booking_status"] == "CANCELLED"
        assert cancel_data["booking_id"] == booking_id

        # SQL Database Verification
        db_cancel = db_helper.get_cancellation_for_booking(booking_id)
        assert db_cancel is not None
        assert db_cancel["cancellation_reason"] == "Customer changed schedule"

        db_booking = db_helper.get_booking_by_id(booking_id)
        assert db_booking["status"] == "CANCELLED"

    def test_cancel_confirmed_booking_and_inventory_restoration(
        self,
        booking_client: BookingClient,
        payment_client: PaymentClient,
        db_helper: DatabaseHelper
    ):
        """TC-CANCEL-02: Verify cancelling a CONFIRMED booking issues refund and restores seats to inventory."""
        flight_id = 2
        initial_seats = db_helper.get_flight_seats(flight_id)
        passengers = 2

        # 1. Create booking
        booking_res = booking_client.create_booking(
            booking_type="FLIGHT",
            item_id=flight_id,
            passengers_or_guests=passengers
        )
        assert booking_res.status_code == 201
        booking_id = booking_res.json()["id"]
        total_price = booking_res.json()["total_price"]

        # Seats should be deducted
        assert db_helper.get_flight_seats(flight_id) == initial_seats - passengers

        # 2. Pay and confirm booking
        pay_res = payment_client.process_payment(booking_id=booking_id, amount=total_price)
        assert pay_res.status_code == 200

        # 3. Cancel booking
        cancel_res = booking_client.cancel_booking(
            booking_id=booking_id,
            reason="Trip canceled by passenger"
        )
        assert_status_code(cancel_res, 200)
        cancel_data = cancel_res.json()
        assert cancel_data["refund_amount"] == total_price
        assert cancel_data["refund_status"] == "PROCESSED"

        # 4. Database Check: Inventory seats restored
        restored_seats = db_helper.get_flight_seats(flight_id)
        assert restored_seats == initial_seats, (
            f"Expected flight seats to be restored to {initial_seats}, but found {restored_seats}"
        )

    def test_cancel_twice_bad_request(self, booking_client: BookingClient):
        """TC-CANCEL-03: Verify cancelling an already cancelled booking returns 400 Bad Request."""
        # Create booking
        b_res = booking_client.create_booking(booking_type="HOTEL", item_id=1, passengers_or_guests=1)
        booking_id = b_res.json()["id"]

        # First cancellation
        cancel_1 = booking_client.cancel_booking(booking_id=booking_id, reason="Reason 1")
        assert_status_code(cancel_1, 200)

        # Second cancellation attempt
        cancel_2 = booking_client.cancel_booking(booking_id=booking_id, reason="Reason 2")
        assert_status_code(cancel_2, 400)
        assert "Booking is already cancelled. Cannot cancel twice." in cancel_2.json()["detail"]

    def test_cancel_nonexistent_booking(self, booking_client: BookingClient):
        """TC-CANCEL-04: Verify cancelling a non-existent booking returns 404 Not Found."""
        response = booking_client.cancel_booking(booking_id=77777, reason="Does not exist")
        assert_status_code(response, 404)
        assert "not found" in response.json()["detail"].lower()
