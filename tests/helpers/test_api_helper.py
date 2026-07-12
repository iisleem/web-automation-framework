import json

import pytest

from utils.helpers.api import ApiClient, assert_json_field, assert_status_code


pytestmark = pytest.mark.helpers


class FakeResponse:
    def __init__(self, status_code=200, body=None, text=None, headers=None):
        self.status_code = status_code
        self._body = body
        self.text = text if text is not None else json.dumps(body)
        self.headers = headers or {"content-type": "application/json"}

    def json(self):
        if self._body is None:
            raise ValueError("No JSON")
        return self._body


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.requests = []

    def request(self, method, url, headers=None, timeout=None, **kwargs):
        self.requests.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self.response


def test_api_client_builds_url_and_merges_headers():
    session = FakeSession(FakeResponse(body={"id": 1, "user": {"name": "Alex"}}))
    client = ApiClient(
        base_url="https://api.example.com",
        default_headers={"Authorization": "Bearer token"},
        session=session,
    )

    response = client.get("/users/1", headers={"X-Test": "true"})

    assert response.status_code == 200
    assert response.body["id"] == 1
    assert session.requests[0]["method"] == "GET"
    assert session.requests[0]["url"] == "https://api.example.com/users/1"
    assert session.requests[0]["headers"] == {
        "Authorization": "Bearer token",
        "X-Test": "true",
    }


def test_api_assertions_pass_for_expected_status_and_json_field():
    response = FakeSession(FakeResponse(body={"user": {"name": "Alex"}})).response
    api_response = ApiClient("https://api.example.com", session=FakeSession(response)).get("user")

    assert_status_code(api_response, 200)
    assert_json_field(api_response, "user.name", "Alex")


def test_assert_status_code_has_clear_failure_message():
    response = FakeSession(FakeResponse(status_code=500, body={"error": "boom"})).response
    api_response = ApiClient("https://api.example.com", session=FakeSession(response)).get("health")

    with pytest.raises(AssertionError, match="Expected status code 200"):
        assert_status_code(api_response, 200)


def test_assert_json_field_supports_list_indexes():
    response = FakeSession(FakeResponse(body={"items": [{"name": "First"}]})).response
    api_response = ApiClient("https://api.example.com", session=FakeSession(response)).get("items")

    assert_json_field(api_response, "items.0.name", "First")
