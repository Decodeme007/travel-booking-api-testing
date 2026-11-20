import pytest
from framework.api_clients.hotel_client import HotelClient
from framework.schemas.hotel_schema import HOTEL_SEARCH_RESPONSE_SCHEMA, HOTEL_ITEM_SCHEMA
from framework.utils.assertions import assert_status_code, assert_json_schema, assert_response_time
from framework.utils.data_generator import generate_future_date, generate_past_date


class TestHotelSearchAPI:
    """SDET Test Suite for Hotel Search API scenarios."""

    def test_search_hotels_valid(self, hotel_client: HotelClient):
        """TC-HOTEL-01: Verify valid hotel search returns matching hotels, correct schema and within SLA."""
        checkin = generate_future_date(3)
        checkout = generate_future_date(7)
        response = hotel_client.search_hotels(
            city="Los Angeles",
            checkin_date=checkin,
            checkout_date=checkout,
            guests=2
        )
        assert_status_code(response, 200)
        assert_response_time(response)
        assert_json_schema(response, HOTEL_SEARCH_RESPONSE_SCHEMA)

        data = response.json()
        assert data["total_hotels"] >= 1
        for hotel in data["hotels"]:
            assert "los angeles" in hotel["city"].lower()
            assert hotel["available_rooms"] >= 1

    def test_search_hotels_invalid_city_numeric(self, hotel_client: HotelClient):
        """TC-HOTEL-02: Verify numeric city returns 400 Bad Request."""
        checkin = generate_future_date(3)
        checkout = generate_future_date(7)
        response = hotel_client.search_hotels(
            city="12345",
            checkin_date=checkin,
            checkout_date=checkout
        )
        assert_status_code(response, 400)
        assert "Invalid city location" in response.json()["detail"]

    def test_search_hotels_checkout_before_checkin(self, hotel_client: HotelClient):
        """TC-HOTEL-03: Verify check-out earlier than check-in returns 400 Bad Request."""
        checkin = generate_future_date(10)
        checkout = generate_future_date(5)
        response = hotel_client.search_hotels(
            city="Los Angeles",
            checkin_date=checkin,
            checkout_date=checkout
        )
        assert_status_code(response, 400)
        assert "Check-out date must be after check-in date" in response.json()["detail"]

    def test_search_hotels_checkin_equals_checkout(self, hotel_client: HotelClient):
        """TC-HOTEL-04: Verify same check-in and check-out date returns 400 Bad Request."""
        same_date = generate_future_date(5)
        response = hotel_client.search_hotels(
            city="Los Angeles",
            checkin_date=same_date,
            checkout_date=same_date
        )
        assert_status_code(response, 400)
        assert "Check-out date must be after check-in date" in response.json()["detail"]

    def test_search_hotels_past_checkin_date(self, hotel_client: HotelClient):
        """TC-HOTEL-05: Verify check-in date in the past returns 400 Bad Request."""
        past_checkin = generate_past_date(2)
        future_checkout = generate_future_date(4)
        response = hotel_client.search_hotels(
            city="Los Angeles",
            checkin_date=past_checkin,
            checkout_date=future_checkout
        )
        assert_status_code(response, 400)
        assert "Check-in date cannot be in the past" in response.json()["detail"]

    def test_search_hotels_missing_city(self, hotel_client: HotelClient):
        """TC-HOTEL-06: Verify missing required city returns 422 Unprocessable Entity."""
        checkin = generate_future_date(3)
        checkout = generate_future_date(7)
        response = hotel_client.search_hotels(
            city=None,
            checkin_date=checkin,
            checkout_date=checkout
        )
        assert_status_code(response, 422)

    @pytest.mark.parametrize("invalid_guests", [0, -1, 15])
    def test_search_hotels_invalid_guest_count(self, hotel_client: HotelClient, invalid_guests: int):
        """TC-HOTEL-07: Verify boundary guest counts (1-10 allowed) return 422."""
        checkin = generate_future_date(3)
        checkout = generate_future_date(7)
        response = hotel_client.search_hotels(
            city="Los Angeles",
            checkin_date=checkin,
            checkout_date=checkout,
            guests=invalid_guests
        )
        assert_status_code(response, 422)

    def test_get_hotel_by_id_success(self, hotel_client: HotelClient):
        """TC-HOTEL-08: Verify retrieving single hotel details by ID returns 200."""
        response = hotel_client.get_hotel_details(hotel_id=1)
        assert_status_code(response, 200)
        assert_json_schema(response, HOTEL_ITEM_SCHEMA)
        assert response.json()["id"] == 1

    def test_get_hotel_by_id_not_found(self, hotel_client: HotelClient):
        """TC-HOTEL-09: Verify retrieving non-existent hotel ID returns 404 Not Found."""
        response = hotel_client.get_hotel_details(hotel_id=88888)
        assert_status_code(response, 404)
        assert "not found" in response.json()["detail"].lower()
