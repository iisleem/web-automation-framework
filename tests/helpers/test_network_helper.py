import pytest

from utils.helpers.network import (
    FailedRequest,
    assert_no_failed_requests,
    assert_response_json_field,
    assert_response_status,
    block_resources,
    build_response_predicate,
    mock_response,
    start_failed_request_tracking,
    wait_for_response,
)


pytestmark = pytest.mark.helpers


class FakeRequest:
    def __init__(
        self,
        url="https://api.example.com/users",
        method="GET",
        resource_type="xhr",
        failure=None,
    ):
        self.url = url
        self.method = method
        self.resource_type = resource_type
        self._failure = failure or {"errorText": "net::ERR_FAILED"}

    def failure(self):
        return self._failure


class FakeResponse:
    def __init__(self, url, status=200, body=None, method="GET"):
        self.url = url
        self.status = status
        self._body = body or {}
        self.request = FakeRequest(url=url, method=method)

    def json(self):
        return self._body


class FakeResponseContext:
    def __init__(self, response):
        self.value = response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakePage:
    def __init__(self):
        self.handlers = {}
        self.routes = []
        self.response = FakeResponse(
            "https://api.example.com/orders/123",
            status=201,
            body={"order": {"id": 123}},
            method="POST",
        )

    def on(self, event_name, handler):
        self.handlers[event_name] = handler

    def route(self, url_pattern, handler):
        self.routes.append((url_pattern, handler))

    def expect_response(self, predicate, timeout):
        assert timeout == 5000
        assert predicate(self.response)
        return FakeResponseContext(self.response)

    def wait_for_event(self, event_name, predicate, timeout):
        assert event_name == "response"
        assert timeout == 5000
        assert predicate(self.response)
        return self.response


class FakeRoute:
    def __init__(self, resource_type="xhr"):
        self.request = FakeRequest(resource_type=resource_type)
        self.aborted = False
        self.continued = False
        self.fulfilled = None

    def abort(self):
        self.aborted = True

    def continue_(self):
        self.continued = True

    def fulfill(self, **kwargs):
        self.fulfilled = kwargs


def test_build_response_predicate_matches_url_status_and_method():
    predicate = build_response_predicate(
        url_contains="/orders",
        status=201,
        method="POST",
    )

    assert predicate(FakeResponse("https://api.example.com/orders/123", 201, method="POST"))
    assert not predicate(FakeResponse("https://api.example.com/users/123", 201, method="POST"))


def test_wait_for_response_supports_trigger():
    page = FakePage()
    triggered = {"value": False}

    response = wait_for_response(
        page,
        url_contains="/orders",
        status=201,
        method="POST",
        trigger=lambda: triggered.update(value=True),
        timeout_ms=5000,
    )

    assert response.status == 201
    assert triggered["value"] is True


def test_wait_for_response_without_trigger_uses_page_event():
    page = FakePage()

    response = wait_for_response(
        page,
        url_contains="/orders",
        status=201,
        method="POST",
        timeout_ms=5000,
    )

    assert response.url.endswith("/orders/123")


def test_response_assertions_validate_status_and_json_field():
    response = FakeResponse(
        "https://api.example.com/orders/123",
        status=201,
        body={"order": {"id": 123}},
    )

    assert_response_status(response, 201)
    assert_response_json_field(response, "order.id", 123)


def test_failed_request_tracker_records_and_ignores_patterns():
    page = FakePage()
    tracker = start_failed_request_tracking(
        page,
        ignored_url_patterns=["*analytics*"],
    )

    page.handlers["requestfailed"](FakeRequest(url="https://cdn.example.com/analytics.js"))
    page.handlers["requestfailed"](FakeRequest(url="https://api.example.com/orders"))

    assert len(tracker.failed_requests) == 1
    assert tracker.failed_requests[0].url == "https://api.example.com/orders"


def test_assert_no_failed_requests_has_clear_message():
    failed_requests = [
        FailedRequest(
            url="https://api.example.com/orders",
            method="POST",
            failure_text="net::ERR_FAILED",
        )
    ]

    with pytest.raises(AssertionError, match="Expected no failed network requests"):
        assert_no_failed_requests(failed_requests)


def test_block_resources_aborts_configured_resource_types():
    page = FakePage()
    block_resources(page, resource_types=("image",))

    route = FakeRoute(resource_type="image")
    page.routes[0][1](route)

    assert route.aborted is True
    assert route.continued is False


def test_block_resources_continues_non_blocked_types():
    page = FakePage()
    block_resources(page, resource_types=("image",))

    route = FakeRoute(resource_type="xhr")
    page.routes[0][1](route)

    assert route.continued is True


def test_mock_response_fulfills_route():
    page = FakePage()
    mock_response(page, "**/feature-flags", body='{"enabled": true}', status=200)

    route = FakeRoute()
    page.routes[0][1](route)

    assert route.fulfilled == {
        "status": 200,
        "body": '{"enabled": true}',
        "headers": {"content-type": "application/json"},
    }
