import time
import threading
import socket
import pytest
import uvicorn
import requests
from app.main import app
from app.seed_data import seed_database
from framework.config import API_BASE_URL, TEST_USER, ADMIN_USER
from framework.api_clients.auth_client import AuthClient
from framework.api_clients.flight_client import FlightClient
from framework.api_clients.hotel_client import HotelClient
from framework.api_clients.booking_client import BookingClient
from framework.api_clients.payment_client import PaymentClient
from framework.database.db_helper import DatabaseHelper
from framework.utils.logger import get_logger

logger = get_logger("TestSetup")


def is_port_in_use(host: str, port: int) -> bool:
    """Check if server port is already listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session", autouse=True)
def start_test_server():
    """
    Session-level fixture: ensures API server is running and database is seeded.
    If server is not running on 127.0.0.1:8000, starts it in a background thread.
    """
    # 1. Initialize seed data
    seed_database()

    # 2. Check if server already running
    if not is_port_in_use("127.0.0.1", 8000):
        logger.info("Starting background Uvicorn test server on 127.0.0.1:8000...")
        config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="warning")
        server = uvicorn.Server(config=config)
        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()

        # Wait for server to become healthy
        max_retries = 30
        for _ in range(max_retries):
            try:
                res = requests.get(f"{API_BASE_URL}/health", timeout=1)
                if res.status_code == 200:
                    logger.info("Test server is UP and healthy!")
                    break
            except requests.exceptions.RequestException:
                time.sleep(0.2)
        else:
            raise RuntimeError("Timed out waiting for test server to launch.")
    else:
        logger.info("Server is already running on port 8000.")

    yield


@pytest.fixture(scope="session")
def db_helper():
    """Provides direct database testing helper."""
    return DatabaseHelper()


@pytest.fixture(scope="session")
def auth_client():
    return AuthClient(API_BASE_URL)


@pytest.fixture(scope="session")
def user_token(auth_client):
    """Provides a valid authentication token for standard test user."""
    res = auth_client.login(TEST_USER["username"], TEST_USER["password"])
    assert res.status_code == 200, f"Failed to login test user: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def admin_token(auth_client):
    """Provides a valid authentication token for admin user."""
    res = auth_client.login(ADMIN_USER["username"], ADMIN_USER["password"])
    assert res.status_code == 200, f"Failed to login admin user: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="function")
def flight_client(user_token):
    return FlightClient(API_BASE_URL, token=user_token)


@pytest.fixture(scope="function")
def hotel_client(user_token):
    return HotelClient(API_BASE_URL, token=user_token)


@pytest.fixture(scope="function")
def booking_client(user_token):
    return BookingClient(API_BASE_URL, token=user_token)


@pytest.fixture(scope="function")
def payment_client(user_token):
    return PaymentClient(API_BASE_URL, token=user_token)
