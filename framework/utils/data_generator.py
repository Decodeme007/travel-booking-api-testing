import random
import string
from datetime import datetime, timedelta


def generate_future_date(days_ahead: int = 5) -> str:
    """Returns future date string in YYYY-MM-DD format."""
    return (datetime.utcnow() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")


def generate_past_date(days_ago: int = 5) -> str:
    """Returns past date string in YYYY-MM-DD format."""
    return (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def generate_random_string(length: int = 8) -> str:
    """Generate a random alphanumeric string."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_email() -> str:
    """Generate a unique test email."""
    return f"test_{generate_random_string(6).lower()}@traveltesting.com"
