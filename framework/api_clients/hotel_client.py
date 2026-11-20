from typing import Optional
import requests
from framework.api_clients.base_client import BaseAPIClient


class HotelClient(BaseAPIClient):
    """API Client for Hotel Search and Inspection."""

    def search_hotels(
        self,
        city: Optional[str] = None,
        checkin_date: Optional[str] = None,
        checkout_date: Optional[str] = None,
        guests: Optional[int] = None
    ) -> requests.Response:
        """Search available hotels with query parameters."""
        params = {}
        if city is not None:
            params["city"] = city
        if checkin_date is not None:
            params["checkin_date"] = checkin_date
        if checkout_date is not None:
            params["checkout_date"] = checkout_date
        if guests is not None:
            params["guests"] = guests

        return self.get("/api/v1/hotels/search", params=params)

    def get_hotel_details(self, hotel_id: int) -> requests.Response:
        """Get hotel details by unique ID."""
        return self.get(f"/api/v1/hotels/{hotel_id}")
