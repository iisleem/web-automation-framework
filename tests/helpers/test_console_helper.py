import pytest

from utils.helpers.console import (
    ConsoleEntry,
    assert_no_console_errors,
    filter_console_entries,
    start_console_tracking,
)


pytestmark = pytest.mark.helpers


class FakeConsoleMessage:
    def __init__(self, level="error", text="boom", location=None):
        self._level = level
        self._text = text
        self._location = location or {
            "url": "https://example.test/app.js",
            "lineNumber": 12,
            "columnNumber": 5,
        }

    def type(self):
        return self._level

    def text(self):
        return self._text

    def location(self):
        return self._location


class FakePage:
    def __init__(self):
        self.handlers = {}

    def on(self, event_name, handler):
        self.handlers[event_name] = handler


def test_start_console_tracking_records_console_errors_and_warnings():
    page = FakePage()
    tracker = start_console_tracking(page)

    page.handlers["console"](FakeConsoleMessage(level="error", text="API failed"))
    page.handlers["console"](FakeConsoleMessage(level="warning", text="Deprecated API"))
    page.handlers["console"](FakeConsoleMessage(level="log", text="noise"))

    assert [entry.level for entry in tracker.entries] == ["error", "warning"]
    assert tracker.entries[0].url == "https://example.test/app.js"


def test_console_tracker_ignores_configured_patterns():
    page = FakePage()
    tracker = start_console_tracking(
        page,
        ignored_text_patterns=["*ResizeObserver*"],
    )

    page.handlers["console"](
        FakeConsoleMessage(level="error", text="ResizeObserver loop limit exceeded")
    )

    assert tracker.entries == []


def test_console_tracker_records_page_errors():
    page = FakePage()
    tracker = start_console_tracking(page)

    page.handlers["pageerror"](RuntimeError("Unhandled exception"))

    assert tracker.entries == [
        ConsoleEntry(level="pageerror", text="Unhandled exception")
    ]


def test_assert_no_console_errors_has_clear_message():
    entries = [ConsoleEntry(level="error", text="API failed", url="app.js")]

    with pytest.raises(AssertionError, match="Expected no browser console"):
        assert_no_console_errors(entries)


def test_filter_console_entries_by_level_and_text():
    entries = [
        ConsoleEntry(level="error", text="API failed"),
        ConsoleEntry(level="warning", text="Deprecated API"),
    ]

    assert filter_console_entries(entries, levels=("error",)) == [entries[0]]
    assert filter_console_entries(entries, text_contains="Deprecated") == [entries[1]]


def test_console_tracker_serializes_entries_to_dicts():
    page = FakePage()
    tracker = start_console_tracking(page)

    page.handlers["console"](FakeConsoleMessage(level="error", text="API failed"))

    assert tracker.to_dicts()[0]["text"] == "API failed"
