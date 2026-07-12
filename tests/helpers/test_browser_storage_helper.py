import json

import pytest

from utils.helpers.browser import (
    clear_browser_storage,
    get_local_storage_item,
    read_storage_state,
    save_storage_state,
    set_local_storage_item,
)


pytestmark = pytest.mark.helpers


class FakeContext:
    def __init__(self) -> None:
        self.cookies_cleared = False

    def storage_state(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump({"cookies": [], "origins": []}, file)

    def clear_cookies(self) -> None:
        self.cookies_cleared = True


class FakePage:
    def __init__(self) -> None:
        self.context = FakeContext()
        self.local_storage: dict[str, str] = {}
        self.storage_cleared = False

    def evaluate(self, script: str, arg=None):
        if "clear" in script:
            self.local_storage.clear()
            self.storage_cleared = True
            return None
        if "setItem" in script:
            key, value = arg
            self.local_storage[key] = value
            return None
        if "getItem" in script:
            return self.local_storage.get(arg)
        return None


def test_save_and_read_storage_state(tmp_path):
    page = FakePage()
    state_path = save_storage_state(page, tmp_path / "state.json")

    assert state_path.exists()
    assert read_storage_state(state_path) == {"cookies": [], "origins": []}


def test_set_and_get_local_storage_item():
    page = FakePage()

    set_local_storage_item(page, "token", "abc123")

    assert get_local_storage_item(page, "token") == "abc123"


def test_clear_browser_storage_clears_local_storage_and_cookies():
    page = FakePage()
    page.local_storage["token"] = "abc123"

    clear_browser_storage(page)

    assert page.local_storage == {}
    assert page.storage_cleared is True
    assert page.context.cookies_cleared is True
