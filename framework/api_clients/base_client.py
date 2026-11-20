import json
import requests
from framework.config import API_BASE_URL, DEFAULT_TIMEOUT
from framework.utils.logger import get_logger

logger = get_logger("BaseAPIClient")


class BaseAPIClient:
    """
    Core HTTP Client wrapper for SDET Framework.
    Provides automated logging, latency measurement, header management, and exception safety.
    """

    def __init__(self, base_url: str = API_BASE_URL, token: str = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.token = token
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def set_token(self, token: str):
        """Update bearer token for the session."""
        self.token = token
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        elif "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        data: dict = None,
        json_body: dict = None,
        headers: dict = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> requests.Response:
        """Executes an HTTP request with comprehensive logging."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = dict(self.session.headers)
        if headers:
            merged_headers.update(headers)

        logger.info(f"==> REQUEST: {method.upper()} {url}")
        if params:
            logger.debug(f"    Params: {params}")
        if json_body is not None:
            logger.debug(f"    Body: {json.dumps(json_body)}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_body,
                headers=merged_headers,
                timeout=timeout
            )
            elapsed_ms = response.elapsed.total_seconds() * 1000
            logger.info(
                f"<== RESPONSE: {response.status_code} ({elapsed_ms:.1f}ms) for {method.upper()} {url}"
            )
            logger.debug(f"    Response Content: {response.text[:500]}")
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request to {url} failed: {e}")
            raise

    def get(self, endpoint: str, params: dict = None, headers: dict = None) -> requests.Response:
        return self.request("GET", endpoint, params=params, headers=headers)

    def post(self, endpoint: str, json_body: dict = None, params: dict = None, headers: dict = None) -> requests.Response:
        return self.request("POST", endpoint, params=params, json_body=json_body, headers=headers)

    def put(self, endpoint: str, json_body: dict = None, headers: dict = None) -> requests.Response:
        return self.request("PUT", endpoint, json_body=json_body, headers=headers)

    def delete(self, endpoint: str, headers: dict = None) -> requests.Response:
        return self.request("DELETE", endpoint, headers=headers)
