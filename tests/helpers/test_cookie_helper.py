import pytest

from utils.helpers.cookies import (
    assert_cookie_attribute,
    assert_cookie_exists,
    assert_cookie_value,
    copy_cookies,
    delete_cookie,
    get_cookie,
    get_cookies,
    set_cookie,
)


pytestmark = pytest.mark.helpers


class FakeContext:
    def __init__(self, cookies=None):
        self._cookies = cookies or []
        self.clear_calls = []

    def cookies(self):
        return self._cookies

    def add_cookies(self, cookies):
        self._cookies.extend(cookies)

    def clear_cookies(self, **kwargs):
        self.clear_calls.append(kwargs)
        name = kwargs.get("name")
        if name:
            self._cookies = [cookie for cookie in self._cookies if cookie["name"] != name]
        else:
            self._cookies = []


class FakePage:
    def __init__(self, context):
        self.context = context


def test_get_cookies_supports_page_or_context():
    context = FakeContext(cookies=[{"name": "session", "value": "abc"}])
    page = FakePage(context)

    assert get_cookies(context) == [{"name": "session", "value": "abc"}]
    assert get_cookies(page) == [{"name": "session", "value": "abc"}]


def test_get_cookie_returns_matching_cookie():
    context = FakeContext(cookies=[{"name": "session", "value": "abc"}])

    assert get_cookie(context, "session") == {"name": "session", "value": "abc"}
    assert get_cookie(context, "missing") is None


def test_cookie_assertions_return_cookie():
    context = FakeContext(cookies=[{"name": "session", "value": "abc", "sameSite": "Lax"}])

    assert_cookie_exists(context, "session")
    assert_cookie_value(context, "session", "abc")
    assert_cookie_attribute(context, "session", "sameSite", "Lax")


def test_assert_cookie_value_has_clear_failure_message():
    context = FakeContext(cookies=[{"name": "session", "value": "wrong"}])

    with pytest.raises(AssertionError, match="Expected cookie 'session' value"):
        assert_cookie_value(context, "session", "abc")


def test_set_cookie_adds_playwright_cookie_dict():
    context = FakeContext()

    cookie = set_cookie(
        context,
        name="session",
        value="abc",
        url="https://example.test",
        http_only=True,
        secure=True,
    )

    assert cookie in context.cookies()
    assert cookie["httpOnly"] is True
    assert cookie["secure"] is True
    assert cookie["sameSite"] == "Lax"


def test_delete_cookie_passes_filters_to_context():
    context = FakeContext(cookies=[{"name": "session", "value": "abc"}])

    delete_cookie(context, "session", domain="example.test", path="/")

    assert context.clear_calls == [{"name": "session", "domain": "example.test", "path": "/"}]
    assert context.cookies() == []


def test_copy_cookies_between_contexts():
    source = FakeContext(cookies=[{"name": "session", "value": "abc"}])
    target = FakeContext()

    copied = copy_cookies(source, target)

    assert copied == [{"name": "session", "value": "abc"}]
    assert target.cookies() == copied
