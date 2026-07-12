import pytest

from utils.helpers.security import (
    assert_cookie_security_flags,
    assert_header_present,
    assert_no_sensitive_values_in_storage,
    assert_no_sensitive_values_in_text,
    assert_security_headers,
    get_response_headers,
)


pytestmark = pytest.mark.helpers


class FakeResponse:
    headers = {
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
    }


class FakePage:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def evaluate(self, script):
        return self.snapshot


def test_security_header_helpers_accept_response_or_dict():
    headers = get_response_headers(FakeResponse())

    assert headers["content-security-policy"] == "default-src 'self'"
    assert_security_headers(FakeResponse())
    assert_header_present(FakeResponse(), "x-frame-options")


def test_security_header_assertion_reports_missing_headers():
    with pytest.raises(AssertionError, match="Missing expected security headers"):
        assert_security_headers({"x-frame-options": "DENY"})


def test_cookie_security_flags_validate_selected_cookies():
    cookies = [
        {"name": "session", "secure": True, "httpOnly": True, "sameSite": "Lax"},
        {"name": "prefs", "secure": True, "httpOnly": True, "sameSite": "Strict"},
    ]

    assert_cookie_security_flags(cookies, ["session"])


def test_cookie_security_flags_report_failures():
    cookies = [{"name": "session", "secure": False, "httpOnly": False, "sameSite": "Loose"}]

    with pytest.raises(AssertionError, match="Cookie security flag failures"):
        assert_cookie_security_flags(cookies)


def test_sensitive_value_helpers_detect_leaks():
    assert_no_sensitive_values_in_text("normal page content")
    assert_no_sensitive_values_in_storage(FakePage('{"localStorage": {"theme": "dark"}}'))

    with pytest.raises(AssertionError, match="Sensitive value patterns"):
        assert_no_sensitive_values_in_text("api_token=abc123")

    with pytest.raises(AssertionError, match="browser storage"):
        assert_no_sensitive_values_in_storage(FakePage('{"localStorage": {"token": "abc"}}'))
