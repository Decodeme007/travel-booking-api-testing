import pytest
from framework.api_clients.auth_client import AuthClient
from framework.config import API_BASE_URL, TEST_USER
from framework.schemas.auth_schema import LOGIN_SUCCESS_SCHEMA, USER_PROFILE_SCHEMA
from framework.utils.assertions import assert_status_code, assert_json_schema, assert_response_time
from framework.utils.data_generator import generate_random_string, generate_random_email


class TestAuthenticationAPI:
    """Test Suite for Authentication & Authorization APIs."""

    def test_login_successful(self, auth_client: AuthClient):
        """TC-AUTH-01: Verify successful login returns valid JWT token and 200 OK."""
        response = auth_client.login(TEST_USER["username"], TEST_USER["password"])
        assert_status_code(response, 200)
        assert_response_time(response)
        assert_json_schema(response, LOGIN_SUCCESS_SCHEMA)

        body = response.json()
        assert body["username"] == TEST_USER["username"]
        assert body["token_type"] == "bearer"
        assert len(body["access_token"]) > 20

    def test_login_invalid_password(self, auth_client: AuthClient):
        """TC-AUTH-02: Verify login with incorrect password returns 401 Unauthorized."""
        response = auth_client.login(TEST_USER["username"], "WrongPassword123!")
        assert_status_code(response, 401)
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, auth_client: AuthClient):
        """TC-AUTH-03: Verify login with non-existent username returns 401 Unauthorized."""
        response = auth_client.login("non_existent_user_999", "RandomPassword123!")
        assert_status_code(response, 401)
        assert "Invalid username or password" in response.json()["detail"]

    def test_protected_endpoint_valid_token(self, auth_client: AuthClient, user_token: str):
        """TC-AUTH-04: Verify protected endpoint /me returns user profile with valid token."""
        response = auth_client.get_profile(token=user_token)
        assert_status_code(response, 200)
        assert_json_schema(response, USER_PROFILE_SCHEMA)
        assert response.json()["username"] == TEST_USER["username"]

    def test_protected_endpoint_missing_token(self, auth_client: AuthClient):
        """TC-AUTH-05: Verify accessing protected endpoint without token returns 401 Unauthorized."""
        response = auth_client.get_profile(token=None)
        assert_status_code(response, 401)
        assert "Authentication credentials were not provided" in response.json()["detail"]

    def test_protected_endpoint_invalid_token(self, auth_client: AuthClient):
        """TC-AUTH-06: Verify accessing protected endpoint with malformed token returns 401."""
        response = auth_client.get_profile(token="malformed.invalid.token12345")
        assert_status_code(response, 401)
        assert "Invalid authentication token" in response.json()["detail"]

    def test_protected_endpoint_expired_token(self, auth_client: AuthClient):
        """TC-AUTH-07: Verify accessing protected endpoint with expired token returns 401."""
        expired_token_res = auth_client.get_expired_token(TEST_USER["username"], TEST_USER["password"])
        assert_status_code(expired_token_res, 200)
        expired_token = expired_token_res.json()["expired_token"]

        response = auth_client.get_profile(token=expired_token)
        assert_status_code(response, 401)
        assert "Token has expired" in response.json()["detail"]

    def test_register_new_user(self, auth_client: AuthClient):
        """TC-AUTH-08: Verify successful registration of a new user."""
        random_user = f"user_{generate_random_string(6).lower()}"
        random_email = generate_random_email()
        response = auth_client.register(random_user, random_email, "TestPassSecure123!")

        assert_status_code(response, 201)
        assert_json_schema(response, LOGIN_SUCCESS_SCHEMA)
        assert response.json()["username"] == random_user

    def test_register_duplicate_user(self, auth_client: AuthClient):
        """TC-AUTH-09: Verify registering an existing user returns 409 Conflict."""
        response = auth_client.register(
            TEST_USER["username"],
            "duplicate@traveltest.com",
            "Password123!"
        )
        assert_status_code(response, 409)
        assert "already exists" in response.json()["detail"]
