import json

import pytest

from utils.helpers.auth import (
    assert_storage_state_has_cookies,
    assert_storage_state_has_origin,
    clear_auth_state,
    create_authenticated_state,
    new_context_with_storage,
    storage_state_exists,
)


pytestmark = pytest.mark.helpers


class FakeContext:
    def __init__(self):
        self.state = {
            "cookies": [{"name": "session", "value": "abc123"}],
            "origins": [{"origin": "https://example.test", "localStorage": []}],
        }

    def storage_state(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.state, file)


class FakePage:
    def __init__(self):
        self.context = FakeContext()
        self.logged_in = False
        self.verified = False


class FakeBrowser:
    def __init__(self):
        self.contexts = []

    def new_context(self, **options):
        self.contexts.append(options)
        return options


def test_create_authenticated_state_runs_login_verify_and_saves_state(tmp_path):
    page = FakePage()
    state_path = tmp_path / "auth.json"

    def login_action(page):
        page.logged_in = True

    def verify_action(page):
        assert page.logged_in is True
        page.verified = True

    result = create_authenticated_state(
        page,
        state_path,
        login_action,
        verify_action=verify_action,
    )

    assert result == state_path
    assert page.logged_in is True
    assert page.verified is True
    assert storage_state_exists(state_path)


def test_new_context_with_storage_uses_saved_state(tmp_path):
    state_path = tmp_path / "auth.json"
    state_path.write_text('{"cookies": [], "origins": []}', encoding="utf-8")
    browser = FakeBrowser()

    context = new_context_with_storage(
        browser,
        state_path,
        viewport={"width": 1280, "height": 720},
    )

    assert context["storage_state"] == str(state_path)
    assert context["viewport"] == {"width": 1280, "height": 720}


def test_new_context_with_storage_requires_existing_state(tmp_path):
    with pytest.raises(AssertionError, match="Storage state file does not exist"):
        new_context_with_storage(FakeBrowser(), tmp_path / "missing.json")


def test_storage_state_assertions_validate_cookies_and_origin(tmp_path):
    state_path = tmp_path / "auth.json"
    state_path.write_text(
        json.dumps(
            {
                "cookies": [{"name": "session", "value": "abc123"}],
                "origins": [{"origin": "https://example.test"}],
            }
        ),
        encoding="utf-8",
    )

    assert_storage_state_has_cookies(state_path, ["session"])
    assert_storage_state_has_origin(state_path, "https://example.test")


def test_storage_state_cookie_assertion_has_clear_failure_message(tmp_path):
    state_path = tmp_path / "auth.json"
    state_path.write_text('{"cookies": [], "origins": []}', encoding="utf-8")

    with pytest.raises(AssertionError, match="to contain cookies"):
        assert_storage_state_has_cookies(state_path)


def test_clear_auth_state_deletes_file_when_present(tmp_path):
    state_path = tmp_path / "auth.json"
    state_path.write_text("{}", encoding="utf-8")

    clear_auth_state(state_path)

    assert not state_path.exists()


def test_clear_auth_state_ignores_missing_file(tmp_path):
    clear_auth_state(tmp_path / "missing.json")
