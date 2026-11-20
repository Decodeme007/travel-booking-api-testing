from typing import Optional
import requests
from framework.api_clients.base_client import BaseAPIClient


class FlightClient(BaseAPIClient):
    """API Client for Flight Search and Inspection."""

    def search_flights(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        departure_date: Optional[str] = None,
        return_date: Optional[str] = None,
        passengers: Optional[int] = None
    ) -> requests.Response:
        """Search available flights with query parameters."""
        params = {}
        if origin is not None:
            params["origin"] = origin
        if destination is not None:
            params["destination"] = destination
        if departure_date is not None:
            params["departure_date"] = departure_date
        if return_date is not None:
            params["return_date"] = return_date
        if passengers is not None:
            params["passengers"] = passengers

        return self.get("/api/v1/flights/search", params=params)

    def get_flight_details(self, flight_id: int) -> requests.Response:
        """Get flight by unique ID."""
        return self.get(f"/api/v1/flights/{flight_id}")
