from __future__ import annotations

from typing import Any

from utils.helpers.api.api_client import ApiResponse


def assert_status_code(response: ApiResponse, expected_status_code: int) -> None:
    assert response.status_code == expected_status_code, (
        f"Expected status code {expected_status_code}, got {response.status_code}. "
        f"Response body: {response.text}"
    )


def assert_json_field(
    response: ApiResponse,
    field_path: str,
    expected_value: Any,
) -> None:
    actual_value = _get_nested_value(response.body, field_path)
    assert actual_value == expected_value, (
        f"Expected JSON field '{field_path}' to be {expected_value!r}, got {actual_value!r}"
    )


def _get_nested_value(body: Any, field_path: str) -> Any:
    current = body
    for part in field_path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            current = current[int(part)]
        else:
            return None
    return current
