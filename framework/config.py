import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Test Execution Settings
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "10"))
MAX_RESPONSE_TIME_MS = int(os.getenv("MAX_RESPONSE_TIME_MS", "1500"))

# Database Connection (Default SQLite, supports MySQL via DB_URL)
DB_PATH = BASE_DIR / "travel_booking.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}")

# Test User Credentials
TEST_USER = {
    "username": "testuser",
    "password": "Password123!"
}

ADMIN_USER = {
    "username": "adminuser",
    "password": "AdminSecure2026!"
}
