from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from framework.config import DATABASE_URL
from framework.utils.logger import get_logger

logger = get_logger("DBHelper")


class DatabaseHelper:
    """
    Direct Database testing helper for asserting backend data consistency,
    verifying SQL queries, and cleaning test state.
    """

    def __init__(self, db_url: str = DATABASE_URL):
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        self.engine = create_engine(db_url, connect_args=connect_args)
        self.Session = sessionmaker(bind=self.engine)

    def execute_query(self, query: str, params: dict = None) -> list:
        """Execute a custom SQL SELECT query and return rows as list of dicts."""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            logger.debug(f"Executed SQL: {query} -> Found {len(rows)} records")
            return rows

    def execute_non_query(self, query: str, params: dict = None) -> int:
        """Execute INSERT / UPDATE / DELETE SQL statement."""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            conn.commit()
            return result.rowcount

    def get_booking_by_id(self, booking_id: int) -> dict:
        """Retrieve booking directly from SQL table."""
        rows = self.execute_query(
            "SELECT * FROM bookings WHERE id = :booking_id",
            {"booking_id": booking_id}
        )
        return rows[0] if rows else None

    def get_booking_by_reference(self, reference: str) -> dict:
        """Retrieve booking by booking reference."""
        rows = self.execute_query(
            "SELECT * FROM bookings WHERE booking_reference = :ref",
            {"ref": reference}
        )
        return rows[0] if rows else None

    def get_payment_for_booking(self, booking_id: int) -> dict:
        """Retrieve payment record for a given booking ID."""
        rows = self.execute_query(
            "SELECT * FROM payments WHERE booking_id = :booking_id ORDER BY id DESC",
            {"booking_id": booking_id}
        )
        return rows[0] if rows else None

    def get_cancellation_for_booking(self, booking_id: int) -> dict:
        """Retrieve cancellation record for a given booking ID."""
        rows = self.execute_query(
            "SELECT * FROM cancellations WHERE booking_id = :booking_id",
            {"booking_id": booking_id}
        )
        return rows[0] if rows else None

    def get_flight_seats(self, flight_id: int) -> int:
        """Get current available seats for a flight from database."""
        rows = self.execute_query(
            "SELECT available_seats FROM flights WHERE id = :flight_id",
            {"flight_id": flight_id}
        )
        return rows[0]["available_seats"] if rows else 0

    def cleanup_booking(self, booking_id: int):
        """Clean up booking and its cascading payments and cancellations."""
        self.execute_non_query("DELETE FROM cancellations WHERE booking_id = :id", {"id": booking_id})
        self.execute_non_query("DELETE FROM payments WHERE booking_id = :id", {"id": booking_id})
        self.execute_non_query("DELETE FROM bookings WHERE id = :id", {"id": booking_id})
        logger.info(f"Cleaned up test data for booking ID {booking_id}")
