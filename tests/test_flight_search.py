import pytest
from framework.api_clients.flight_client import FlightClient
from framework.schemas.flight_schema import FLIGHT_SEARCH_RESPONSE_SCHEMA, FLIGHT_ITEM_SCHEMA
from framework.utils.assertions import assert_status_code, assert_json_schema, assert_response_time
from framework.utils.data_generator import generate_future_date, generate_past_date


class TestFlightSearchAPI:
    """SDET Test Suite for Flight Search API scenarios."""

    def test_search_flights_valid(self, flight_client: FlightClient):
        """TC-FLIGHT-01: Verify valid flight search returns matching flights, schema conformity, and passes SLA."""
        dep_date = generate_future_date(5)
        response = flight_client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=dep_date,
            passengers=1
        )
        assert_status_code(response, 200)
        assert_response_time(response)
        assert_json_schema(response, FLIGHT_SEARCH_RESPONSE_SCHEMA)

        data = response.json()
        assert data["total_flights"] >= 1
        for flight in data["flights"]:
            assert flight["origin"] == "JFK"
            assert flight["destination"] == "LAX"
            assert flight["available_seats"] >= 1

    def test_search_flights_with_valid_return_date(self, flight_client: FlightClient):
        """TC-FLIGHT-02: Verify round-trip search with valid departure and return date."""
        dep_date = generate_future_date(5)
        ret_date = generate_future_date(12)
        response = flight_client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=dep_date,
            return_date=ret_date,
            passengers=2
        )
        assert_status_code(response, 200)
        assert_json_schema(response, FLIGHT_SEARCH_RESPONSE_SCHEMA)

    def test_search_flights_missing_destination(self, flight_client: FlightClient):
        """TC-FLIGHT-03: Verify missing required parameter (destination) returns 422 Unprocessable Entity."""
        dep_date = generate_future_date(5)
        response = flight_client.search_flights(
            origin="JFK",
            destination=None,
            departure_date=dep_date
        )
        assert_status_code(response, 422)

    def test_search_flights_missing_origin(self, flight_client: FlightClient):
        """TC-FLIGHT-04: Verify missing required parameter (origin) returns 422 Unprocessable Entity."""
        dep_date = generate_future_date(5)
        response = flight_client.search_flights(
            origin=None,
            destination="LAX",
            departure_date=dep_date
        )
        assert_status_code(response, 422)

    def test_search_flights_past_departure_date(self, flight_client: FlightClient):
        """TC-FLIGHT-05: Verify departure date in the past returns 400 Bad Request."""
        past_date = generate_past_date(3)
        response = flight_client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=past_date
        )
        assert_status_code(response, 400)
        assert "Departure date cannot be in the past" in response.json()["detail"]

    def test_search_flights_return_before_departure(self, flight_client: FlightClient):
        """TC-FLIGHT-06: Verify return date earlier than departure date returns 400 Bad Request."""
        dep_date = generate_future_date(10)
        ret_date = generate_future_date(5)
        response = flight_client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=dep_date,
            return_date=ret_date
        )
        assert_status_code(response, 400)
        assert "Return date cannot be earlier than departure date" in response.json()["detail"]

    @pytest.mark.parametrize("invalid_date", [
        "25-12-2026",
        "2026/12/25",
        "invalid-date",
        "2026-99-99"
    ])
    def test_search_flights_invalid_date_format(self, flight_client: FlightClient, invalid_date: str):
        """TC-FLIGHT-07: Parameterized test verifying invalid date formats return 400 Bad Request."""
        response = flight_client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=invalid_date
        )
        assert_status_code(response, 400)
        assert "Invalid departure_date format" in response.json()["detail"]

    def test_search_flights_same_origin_destination(self, flight_client: FlightClient):
        """TC-FLIGHT-08: Verify origin equal to destination returns 400 Bad Request."""
        dep_date = generate_future_date(5)
        response = flight_client.search_flights(
            origin="JFK",
            destination="JFK",
            departure_date=dep_date
        )
        assert_status_code(response, 400)
        assert "Origin and destination cannot be the same" in response.json()["detail"]

    @pytest.mark.parametrize("invalid_code", ["JF", "NEWYORK", "123", "J1K"])
    def test_search_flights_invalid_airport_code(self, flight_client: FlightClient, invalid_code: str):
        """TC-FLIGHT-09: Verify non-3-letter airport codes return 400 Bad Request."""
        dep_date = generate_future_date(5)
        response = flight_client.search_flights(
            origin=invalid_code,
            destination="LAX",
            departure_date=dep_date
        )
        assert_status_code(response, 400)

    @pytest.mark.parametrize("passengers", [0, -1, 11])
    def test_search_flights_invalid_passenger_boundaries(self, flight_client: FlightClient, passengers: int):
        """TC-FLIGHT-10: Verify boundary passenger counts (1-10 allowed) return 422."""
        dep_date = generate_future_date(5)
        response = flight_client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=dep_date,
            passengers=passengers
        )
        assert_status_code(response, 422)

    def test_get_flight_by_id_success(self, flight_client: FlightClient):
        """TC-FLIGHT-11: Verify retrieving single flight by valid ID returns 200."""
        response = flight_client.get_flight_details(flight_id=1)
        assert_status_code(response, 200)
        assert_json_schema(response, FLIGHT_ITEM_SCHEMA)
        assert response.json()["id"] == 1

    def test_get_flight_by_id_not_found(self, flight_client: FlightClient):
        """TC-FLIGHT-12: Verify retrieving non-existent flight ID returns 404 Not Found."""
        response = flight_client.get_flight_details(flight_id=99999)
        assert_status_code(response, 404)
        assert "not found" in response.json()["detail"].lower()
