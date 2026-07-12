from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import Any, Callable


ResponsePredicate = Callable[[Any], bool]


@dataclass(frozen=True)
class FailedRequest:
    url: str
    method: str
    failure_text: str


class FailedRequestTracker:
    def __init__(self, ignored_url_patterns: list[str] | None = None) -> None:
        self.ignored_url_patterns = ignored_url_patterns or []
        self.failed_requests: list[FailedRequest] = []

    def record(self, request: Any) -> None:
        url = getattr(request, "url", "")
        if _matches_any(url, self.ignored_url_patterns):
            return

        failure = request.failure
        if callable(failure):
            failure = failure()
        self.failed_requests.append(
            FailedRequest(
                url=url,
                method=getattr(request, "method", ""),
                failure_text=_failure_text(failure),
            )
        )

    def assert_no_failures(self) -> None:
        assert_no_failed_requests(self.failed_requests)


def wait_for_response(
    page: Any,
    *,
    url_contains: str | None = None,
    status: int | None = None,
    method: str | None = None,
    predicate: ResponsePredicate | None = None,
    trigger: Callable[[], Any] | None = None,
    timeout_ms: int = 10000,
) -> Any:
    response_predicate = build_response_predicate(
        url_contains=url_contains,
        status=status,
        method=method,
        predicate=predicate,
    )

    if trigger is not None:
        with page.expect_response(response_predicate, timeout=timeout_ms) as response_info:
            trigger()
        return response_info.value

    return page.wait_for_event(
        "response",
        predicate=response_predicate,
        timeout=timeout_ms,
    )


def build_response_predicate(
    *,
    url_contains: str | None = None,
    status: int | None = None,
    method: str | None = None,
    predicate: ResponsePredicate | None = None,
) -> ResponsePredicate:
    def matches(response: Any) -> bool:
        if url_contains and url_contains not in getattr(response, "url", ""):
            return False
        if status is not None and getattr(response, "status", None) != status:
            return False
        if method and _response_method(response).upper() != method.upper():
            return False
        if predicate and not predicate(response):
            return False
        return True

    return matches


def assert_response_status(response: Any, expected_status: int) -> Any:
    actual_status = getattr(response, "status", None)
    assert actual_status == expected_status, (
        f"Expected response status {expected_status}, got {actual_status} for "
        f"{getattr(response, 'url', '<unknown url>')}"
    )
    return response


def response_json(response: Any) -> Any:
    return response.json()


def assert_response_json_field(
    response: Any,
    field_path: str,
    expected_value: Any,
) -> Any:
    body = response_json(response)
    actual_value = _get_nested_value(body, field_path)
    assert actual_value == expected_value, (
        f"Expected response JSON field '{field_path}' to be {expected_value!r}, "
        f"got {actual_value!r}"
    )
    return response


def start_failed_request_tracking(
    page: Any,
    ignored_url_patterns: list[str] | None = None,
) -> FailedRequestTracker:
    tracker = FailedRequestTracker(ignored_url_patterns=ignored_url_patterns)
    page.on("requestfailed", tracker.record)
    return tracker


def assert_no_failed_requests(failed_requests: list[FailedRequest]) -> None:
    assert not failed_requests, _format_failed_requests(failed_requests)


def block_resources(
    page: Any,
    resource_types: tuple[str, ...] = ("image", "font", "media"),
    url_pattern: str = "**/*",
) -> None:
    blocked_types = set(resource_types)

    def handle_route(route: Any) -> None:
        if route.request.resource_type in blocked_types:
            route.abort()
            return
        route.continue_()

    page.route(url_pattern, handle_route)


def mock_response(
    page: Any,
    url_pattern: str,
    *,
    body: str,
    status: int = 200,
    content_type: str = "application/json",
    headers: dict[str, str] | None = None,
) -> None:
    response_headers = {"content-type": content_type, **(headers or {})}

    def handle_route(route: Any) -> None:
        route.fulfill(status=status, body=body, headers=response_headers)

    page.route(url_pattern, handle_route)


def _response_method(response: Any) -> str:
    request = getattr(response, "request", None)
    if request is None:
        return ""
    return getattr(request, "method", "")


def _get_nested_value(body: Any, field_path: str) -> Any:
    value = body
    for part in field_path.split("."):
        if isinstance(value, list):
            value = value[int(part)]
        else:
            value = value[part]
    return value


def _format_failed_requests(failed_requests: list[FailedRequest]) -> str:
    lines = ["Expected no failed network requests, found:"]
    lines.extend(
        f"- {request.method} {request.url}: {request.failure_text}"
        for request in failed_requests
    )
    return "\n".join(lines)


def _failure_text(failure: Any) -> str:
    if isinstance(failure, dict):
        return str(failure.get("errorText", "unknown failure"))
    if failure:
        return str(failure)
    return "unknown failure"


def _matches_any(value: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(value, pattern) for pattern in patterns)
