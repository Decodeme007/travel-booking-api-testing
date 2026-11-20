import requests
from framework.api_clients.base_client import BaseAPIClient


class AuthClient(BaseAPIClient):
    """API Client for Authentication service."""

    def login(self, username: str, password: str) -> requests.Response:
        """Authenticate user and retrieve JWT token."""
        payload = {"username": username, "password": password}
        return self.post("/api/v1/auth/login", json_body=payload)

    def register(self, username: str, email: str, password: str, role: str = "customer") -> requests.Response:
        """Register a new user account."""
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
        return self.post("/api/v1/auth/register", json_body=payload)

    def get_profile(self, token: str = None) -> requests.Response:
        """Get profile of currently authenticated user."""
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.get("/api/v1/auth/me", headers=headers)

    def get_expired_token(self, username: str, password: str) -> requests.Response:
        """Utility for obtaining a signed expired token for negative testing."""
        payload = {"username": username, "password": password}
        return self.post("/api/v1/auth/expired-token-simulate", json_body=payload)
