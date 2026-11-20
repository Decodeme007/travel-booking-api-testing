import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration: defaults to SQLite, seamlessly switches to MySQL via DATABASE_URL
DEFAULT_DB_PATH = BASE_DIR / "travel_booking.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "sdet-travel-booking-secret-key-super-secure-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Server settings
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
