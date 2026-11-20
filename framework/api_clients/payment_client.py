from typing import Optional
import requests
from framework.api_clients.base_client import BaseAPIClient


class PaymentClient(BaseAPIClient):
    """API Client for Payment processing simulation."""

    def process_payment(
        self,
        booking_id: int,
        amount: float,
        currency: str = "USD",
        payment_method: str = "credit_card",
        card_number: Optional[str] = None,
        token: Optional[str] = None
    ) -> requests.Response:
        """Submit payment transaction for booking."""
        payload = {
            "booking_id": booking_id,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method
        }
        if card_number:
            payload["card_number"] = card_number

        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.post("/api/v1/payments/process", json_body=payload, headers=headers)

    def get_payment_details(self, payment_id: int, token: Optional[str] = None) -> requests.Response:
        """Get payment receipt by ID."""
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.get(f"/api/v1/payments/{payment_id}", headers=headers)
