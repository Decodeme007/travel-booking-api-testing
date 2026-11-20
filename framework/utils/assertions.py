import jsonschema
import requests
from framework.config import MAX_RESPONSE_TIME_MS
from framework.utils.logger import get_logger

logger = get_logger("AssertionHelper")


def assert_status_code(response: requests.Response, expected_code: int):
    """Assert HTTP response status code matches expectation with verbose logging."""
    actual_code = response.status_code
    if actual_code != expected_code:
        logger.error(
            f"Status Code Mismatch! Expected: {expected_code}, Got: {actual_code}. Response: {response.text}"
        )
    assert actual_code == expected_code, (
        f"Expected status {expected_code}, but got {actual_code}. Body: {response.text}"
    )


def assert_json_schema(response: requests.Response, expected_schema: dict):
    """Validate that response JSON strictly conforms to the expected JSON schema."""
    try:
        json_data = response.json()
    except Exception as e:
        logger.error(f"Failed to parse JSON response: {e}. Raw content: {response.text}")
        raise AssertionError(f"Response is not valid JSON: {response.text}")

    try:
        jsonschema.validate(instance=json_data, schema=expected_schema)
        logger.debug("JSON schema validation passed.")
    except jsonschema.ValidationError as err:
        logger.error(f"Schema Validation Error: {err.message} on path: {list(err.path)}")
        raise AssertionError(f"JSON Schema Validation Failed: {err.message} on path {list(err.path)}")


def assert_response_time(response: requests.Response, max_latency_ms: int = MAX_RESPONSE_TIME_MS):
    """Assert response time is within acceptable SLA limit."""
    elapsed_ms = response.elapsed.total_seconds() * 1000
    if elapsed_ms > max_latency_ms:
        logger.warning(f"SLA Breached! Elapsed: {elapsed_ms:.2f}ms > Max: {max_latency_ms}ms")
    assert elapsed_ms <= max_latency_ms, (
        f"Response time SLA exceeded! Expected <= {max_latency_ms}ms, but took {elapsed_ms:.2f}ms"
    )
