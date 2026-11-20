from typing import Optional
import requests
from framework.api_clients.base_client import BaseAPIClient


class BookingClient(BaseAPIClient):
    """API Client for Travel Bookings & Cancellations."""

    def create_booking(
        self,
        booking_type: str,
        item_id: int,
        passengers_or_guests: int = 1,
        client_reference_id: Optional[str] = None,
        token: Optional[str] = None
    ) -> requests.Response:
        """Create a new booking."""
        payload = {
            "booking_type": booking_type,
            "item_id": item_id,
            "passengers_or_guests": passengers_or_guests
        }
        if client_reference_id:
            payload["client_reference_id"] = client_reference_id

        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.post("/api/v1/bookings", json_body=payload, headers=headers)

    def get_booking(self, booking_id: int, token: Optional[str] = None) -> requests.Response:
        """Get booking details by ID."""
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.get(f"/api/v1/bookings/{booking_id}", headers=headers)

    def get_booking_status(self, booking_id: int, token: Optional[str] = None) -> requests.Response:
        """Get booking status verification."""
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.get(f"/api/v1/bookings/{booking_id}/status", headers=headers)

    def cancel_booking(
        self,
        booking_id: int,
        reason: str = "Customer requested cancellation",
        token: Optional[str] = None
    ) -> requests.Response:
        """Cancel booking by ID."""
        payload = {"reason": reason}
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.post(f"/api/v1/bookings/{booking_id}/cancel", json_body=payload, headers=headers)
