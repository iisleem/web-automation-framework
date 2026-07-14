from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BrowserTarget:
    name: str
    engine: str
    channel: str | None = None

    @property
    def display_name(self) -> str:
        return self.name


_BROWSER_TARGETS = {
    "chromium": BrowserTarget(name="chromium", engine="chromium"),
    "firefox": BrowserTarget(name="firefox", engine="firefox"),
    "webkit": BrowserTarget(name="webkit", engine="webkit"),
    "chrome": BrowserTarget(name="chrome", engine="chromium", channel="chrome"),
    "msedge": BrowserTarget(name="msedge", engine="chromium", channel="msedge"),
    "safari": BrowserTarget(name="safari", engine="webkit"),
}

VALID_BROWSER_NAMES = frozenset(_BROWSER_TARGETS)
DEFAULT_BROWSER_NAMES = frozenset({"chromium", "firefox", "webkit"})
OPTIONAL_CHANNEL_NAMES = frozenset({"chrome", "msedge"})


def resolve_browser_target(browser_name: str) -> BrowserTarget:
    try:
        return _BROWSER_TARGETS[browser_name]
    except KeyError as error:
        valid = ", ".join(sorted(VALID_BROWSER_NAMES))
        raise ValueError(f"Invalid browser '{browser_name}'. Valid browsers: {valid}") from error


def append_pytest_browser_args(command: list[str], browser_name: str) -> None:
    target = resolve_browser_target(browser_name)
    command.extend(["--browser", target.engine])
    if target.channel:
        command.extend(["--browser-channel", target.channel])


def channel_install_hint(channel: str) -> str:
    if channel == "chrome":
        return "Install Google Chrome or run: python -m playwright install chrome"
    if channel == "msedge":
        return "Install Microsoft Edge or run: python -m playwright install msedge"
    return f"Install the Playwright browser channel: {channel}"


def channel_error_message(browser_name: str) -> str:
    target = resolve_browser_target(browser_name)
    if not target.channel:
        return ""
    return (
        f"Browser '{browser_name}' uses Playwright channel '{target.channel}' on the Chromium engine. "
        f"{channel_install_hint(target.channel)}. The framework uses Playwright --browser-channel; "
        "it does not call system browser CLIs directly."
    )


def channel_preflight_failure(browser_name: str) -> str | None:
    target = resolve_browser_target(browser_name)
    if not target.channel:
        return None

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            is_browser_channel_available(playwright, browser_name)
    except Exception as error:
        return f"{channel_error_message(browser_name)}\nPlaywright reason: {error}"
    return None


def browser_artifact_name(browser_name: str) -> str:
    return resolve_browser_target(browser_name).display_name


def is_browser_channel_available(playwright, browser_name: str) -> bool:
    target = resolve_browser_target(browser_name)
    if not target.channel:
        executable_path = Path(getattr(playwright, target.engine).executable_path)
        return executable_path.exists()
    browser = getattr(playwright, target.engine).launch(channel=target.channel, headless=True)
    browser.close()
    return True
