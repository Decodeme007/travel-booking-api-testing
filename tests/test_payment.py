import pytest
from framework.api_clients.booking_client import BookingClient
from framework.api_clients.payment_client import PaymentClient
from framework.database.db_helper import DatabaseHelper
from framework.schemas.payment_schema import PAYMENT_SUCCESS_SCHEMA
from framework.utils.assertions import assert_status_code, assert_json_schema, assert_response_time


class TestPaymentAPI:
    """SDET Test Suite for Payment Simulation and Transaction Verification."""

    @pytest.fixture
    def active_booking(self, booking_client: BookingClient) -> dict:
        """Helper fixture to create a fresh pending booking for payment tests."""
        res = booking_client.create_booking(
            booking_type="FLIGHT",
            item_id=1,
            passengers_or_guests=1
        )
        assert res.status_code == 201
        return res.json()

    def test_payment_successful_and_db_verification(
        self,
        payment_client: PaymentClient,
        booking_client: BookingClient,
        active_booking: dict,
        db_helper: DatabaseHelper
    ):
        """TC-PAY-01: Verify successful payment updates booking to CONFIRMED and persists in SQL."""
        booking_id = active_booking["id"]
        exact_amount = active_booking["total_price"]

        response = payment_client.process_payment(
            booking_id=booking_id,
            amount=exact_amount,
            payment_method="credit_card",
            currency="USD"
        )
        assert_status_code(response, 200)
        assert_response_time(response)
        assert_json_schema(response, PAYMENT_SUCCESS_SCHEMA)

        payment_data = response.json()
        assert payment_data["status"] == "SUCCESS"
        assert payment_data["booking_id"] == booking_id

        # Database Consistency: Verify SQL records
        db_payment = db_helper.get_payment_for_booking(booking_id)
        assert db_payment is not None, "Payment record missing from SQL table!"
        assert db_payment["status"] == "SUCCESS"
        assert db_payment["amount"] == exact_amount

        db_booking = db_helper.get_booking_by_id(booking_id)
        assert db_booking["status"] == "CONFIRMED", "Booking status in DB did not update to CONFIRMED!"

    def test_payment_failed_simulation(
        self,
        payment_client: PaymentClient,
        active_booking: dict,
        db_helper: DatabaseHelper
    ):
        """TC-PAY-02: Verify card decline simulation results in 402 and booking remains PENDING."""
        booking_id = active_booking["id"]
        exact_amount = active_booking["total_price"]

        response = payment_client.process_payment(
            booking_id=booking_id,
            amount=exact_amount,
            card_number="4000000000000002"  # Declining test card
        )
        assert_status_code(response, 402)

        # Database Check: Payment should be recorded as FAILED, Booking remains PENDING
        db_payment = db_helper.get_payment_for_booking(booking_id)
        assert db_payment is not None
        assert db_payment["status"] == "FAILED"
        assert "declined" in db_payment["failure_reason"].lower()

        db_booking = db_helper.get_booking_by_id(booking_id)
        assert db_booking["status"] == "PENDING"

    def test_payment_mismatched_amount(self, payment_client: PaymentClient, active_booking: dict):
        """TC-PAY-03: Verify payment with mismatched total amount returns 400 Bad Request."""
        booking_id = active_booking["id"]
        wrong_amount = active_booking["total_price"] + 50.00

        response = payment_client.process_payment(
            booking_id=booking_id,
            amount=wrong_amount
        )
        assert_status_code(response, 400)
        assert "does not match booking total" in response.json()["detail"]

    @pytest.mark.parametrize("invalid_amount", [0, -100.50])
    def test_payment_negative_or_zero_amount(
        self,
        payment_client: PaymentClient,
        active_booking: dict,
        invalid_amount: float
    ):
        """TC-PAY-04: Verify non-positive payment amounts return 400 Bad Request."""
        response = payment_client.process_payment(
            booking_id=active_booking["id"],
            amount=invalid_amount
        )
        assert_status_code(response, 400)
        assert "greater than zero" in response.json()["detail"]

    def test_payment_already_paid_booking(
        self,
        payment_client: PaymentClient,
        active_booking: dict
    ):
        """TC-PAY-05: Verify attempting to pay twice for an already CONFIRMED booking returns 400."""
        booking_id = active_booking["id"]
        amount = active_booking["total_price"]

        # First payment succeeds
        res1 = payment_client.process_payment(booking_id=booking_id, amount=amount)
        assert_status_code(res1, 200)

        # Second payment attempt fails
        res2 = payment_client.process_payment(booking_id=booking_id, amount=amount)
        assert_status_code(res2, 400)
        assert "already paid and confirmed" in res2.json()["detail"]

    def test_payment_nonexistent_booking(self, payment_client: PaymentClient):
        """TC-PAY-06: Verify payment for non-existent booking returns 404 Not Found."""
        response = payment_client.process_payment(
            booking_id=99999,
            amount=100.00
        )
        assert_status_code(response, 404)
        assert "not found" in response.json()["detail"].lower()
