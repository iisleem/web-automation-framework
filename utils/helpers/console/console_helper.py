from __future__ import annotations

import fnmatch
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ConsoleEntry:
    level: str
    text: str
    url: str = ""
    line_number: int | None = None
    column_number: int | None = None


class ConsoleTracker:
    def __init__(
        self,
        ignored_text_patterns: list[str] | None = None,
        tracked_levels: tuple[str, ...] = ("error", "warning"),
    ) -> None:
        self.ignored_text_patterns = ignored_text_patterns or []
        self.tracked_levels = tracked_levels
        self.entries: list[ConsoleEntry] = []

    def record_console_message(self, message: Any) -> None:
        level = _call_or_value(message, "type")
        text = _call_or_value(message, "text")
        if level not in self.tracked_levels or _matches_any(text, self.ignored_text_patterns):
            return

        location = _call_or_value(message, "location") or {}
        self.entries.append(
            ConsoleEntry(
                level=level,
                text=text,
                url=str(location.get("url", "")),
                line_number=location.get("lineNumber"),
                column_number=location.get("columnNumber"),
            )
        )

    def record_page_error(self, error: Any) -> None:
        text = str(error)
        if _matches_any(text, self.ignored_text_patterns):
            return
        self.entries.append(ConsoleEntry(level="pageerror", text=text))

    def assert_no_errors(self) -> None:
        assert_no_console_errors(self.entries)

    def to_dicts(self) -> list[dict]:
        return [asdict(entry) for entry in self.entries]


def start_console_tracking(
    page: Any,
    ignored_text_patterns: list[str] | None = None,
    tracked_levels: tuple[str, ...] = ("error", "warning"),
    include_page_errors: bool = True,
) -> ConsoleTracker:
    tracker = ConsoleTracker(
        ignored_text_patterns=ignored_text_patterns,
        tracked_levels=tracked_levels,
    )
    page.on("console", tracker.record_console_message)
    if include_page_errors:
        page.on("pageerror", tracker.record_page_error)
    return tracker


def assert_no_console_errors(entries: list[ConsoleEntry]) -> None:
    assert not entries, _format_console_entries(entries)


def filter_console_entries(
    entries: list[ConsoleEntry],
    *,
    levels: tuple[str, ...] | None = None,
    text_contains: str | None = None,
) -> list[ConsoleEntry]:
    filtered = entries
    if levels is not None:
        filtered = [entry for entry in filtered if entry.level in levels]
    if text_contains is not None:
        filtered = [entry for entry in filtered if text_contains in entry.text]
    return filtered


def _format_console_entries(entries: list[ConsoleEntry]) -> str:
    lines = ["Expected no browser console errors/warnings, found:"]
    for entry in entries:
        location = ""
        if entry.url:
            location = f" ({entry.url}:{entry.line_number or 0}:{entry.column_number or 0})"
        lines.append(f"- {entry.level}: {entry.text}{location}")
    return "\n".join(lines)


def _call_or_value(target: Any, name: str) -> Any:
    value = getattr(target, name, None)
    if callable(value):
        return value()
    return value


def _matches_any(value: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(value, pattern) for pattern in patterns)
