import pytest
from framework.api_clients.booking_client import BookingClient
from framework.api_clients.payment_client import PaymentClient
from framework.schemas.booking_schema import BOOKING_STATUS_SCHEMA
from framework.utils.assertions import assert_status_code, assert_json_schema, assert_response_time


class TestBookingStatusAPI:
    """SDET Test Suite for Booking Status Verification & Lifecycle Transitions."""

    def test_booking_status_lifecycle_transitions(
        self,
        booking_client: BookingClient,
        payment_client: PaymentClient
    ):
        """TC-STATUS-01: Verify status transitions PENDING -> CONFIRMED -> CANCELLED."""
        # 1. Create booking -> PENDING
        create_res = booking_client.create_booking(booking_type="FLIGHT", item_id=1, passengers_or_guests=1)
        assert create_res.status_code == 201
        booking_id = create_res.json()["id"]
        total_price = create_res.json()["total_price"]

        status_res_1 = booking_client.get_booking_status(booking_id)
        assert_status_code(status_res_1, 200)
        assert_response_time(status_res_1)
        assert_json_schema(status_res_1, BOOKING_STATUS_SCHEMA)
        assert status_res_1.json()["status"] == "PENDING"
        assert status_res_1.json()["payment_status"] is None

        # 2. Process Payment -> CONFIRMED
        pay_res = payment_client.process_payment(booking_id=booking_id, amount=total_price)
        assert pay_res.status_code == 200

        status_res_2 = booking_client.get_booking_status(booking_id)
        assert_status_code(status_res_2, 200)
        assert status_res_2.json()["status"] == "CONFIRMED"
        assert status_res_2.json()["payment_status"] == "SUCCESS"

        # 3. Cancel Booking -> CANCELLED
        cancel_res = booking_client.cancel_booking(booking_id=booking_id, reason="Customer canceled")
        assert cancel_res.status_code == 200

        status_res_3 = booking_client.get_booking_status(booking_id)
        assert_status_code(status_res_3, 200)
        assert status_res_3.json()["status"] == "CANCELLED"
        assert status_res_3.json()["cancellation_status"] == "PROCESSED"

    def test_booking_status_admin_access(
        self,
        booking_client: BookingClient,
        admin_token: str
    ):
        """TC-STATUS-02: Verify admin user can inspect any customer booking status."""
        create_res = booking_client.create_booking(booking_type="HOTEL", item_id=1, passengers_or_guests=1)
        booking_id = create_res.json()["id"]

        # Request status using admin token
        response = booking_client.get_booking_status(booking_id=booking_id, token=admin_token)
        assert_status_code(response, 200)
        assert response.json()["booking_id"] == booking_id

    def test_booking_status_not_found(self, booking_client: BookingClient):
        """TC-STATUS-03: Verify checking status of non-existent booking returns 404."""
        response = booking_client.get_booking_status(booking_id=98765)
        assert_status_code(response, 404)
