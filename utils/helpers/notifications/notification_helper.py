from __future__ import annotations

from typing import Any


DEFAULT_NOTIFICATION_SELECTOR = (
    "[role='alert'], [role='status'], [data-test*='toast'], "
    "[data-test*='notification'], .toast, .notification, .snackbar"
)


def notification_locator(
    page: Any,
    *,
    selector: str = DEFAULT_NOTIFICATION_SELECTOR,
    text: str | None = None,
) -> Any:
    locator = page.locator(selector)
    if text:
        locator = locator.filter(has_text=text)
    return locator.first()


def wait_for_notification(
    page: Any,
    *,
    selector: str = DEFAULT_NOTIFICATION_SELECTOR,
    text: str | None = None,
    timeout_ms: int = 5000,
) -> Any:
    locator = notification_locator(page, selector=selector, text=text)
    locator.wait_for(state="visible", timeout=timeout_ms)
    return locator


def assert_notification_visible(
    page: Any,
    expected_text: str | None = None,
    *,
    selector: str = DEFAULT_NOTIFICATION_SELECTOR,
    contains: bool = True,
    timeout_ms: int = 5000,
) -> Any:
    locator = wait_for_notification(
        page,
        selector=selector,
        text=expected_text if contains else None,
        timeout_ms=timeout_ms,
    )
    if expected_text is None:
        return locator

    actual_text = locator.inner_text()
    if contains:
        assert expected_text in actual_text, f"Expected notification to contain {expected_text!r}, got {actual_text!r}"
        return locator
    assert actual_text == expected_text, f"Expected notification to be {expected_text!r}, got {actual_text!r}"
    return locator


def assert_notification_hidden(
    page: Any,
    *,
    selector: str = DEFAULT_NOTIFICATION_SELECTOR,
    text: str | None = None,
    timeout_ms: int = 5000,
) -> None:
    locator = notification_locator(page, selector=selector, text=text)
    locator.wait_for(state="hidden", timeout=timeout_ms)


def dismiss_notification(
    page: Any,
    *,
    dismiss_selector: str,
    notification_selector: str = DEFAULT_NOTIFICATION_SELECTOR,
    timeout_ms: int = 5000,
) -> None:
    page.locator(dismiss_selector).click()
    assert_notification_hidden(
        page,
        selector=notification_selector,
        timeout_ms=timeout_ms,
    )
