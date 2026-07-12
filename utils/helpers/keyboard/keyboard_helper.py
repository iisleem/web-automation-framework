from __future__ import annotations

from typing import Any


def press_key(page: Any, key: str, *, times: int = 1) -> None:
    """Press a keyboard key one or more times."""
    _validate_positive_times(times)
    for _ in range(times):
        page.keyboard.press(key)


def tab_to_next(page: Any, *, times: int = 1) -> None:
    """Move focus forward using the Tab key."""
    press_key(page, "Tab", times=times)


def shift_tab_to_previous(page: Any, *, times: int = 1) -> None:
    """Move focus backward using Shift+Tab."""
    press_key(page, "Shift+Tab", times=times)


def focus_element(page: Any, selector: str) -> Any:
    locator = page.locator(selector)
    locator.focus()
    return locator


def assert_focused(page: Any, selector: str) -> Any:
    locator = page.locator(selector)
    is_focused = locator.evaluate("element => element === document.activeElement")
    assert is_focused, f"Expected element {selector!r} to have browser focus."
    return locator


def assert_focus_order(page: Any, selectors: list[str]) -> None:
    """Press Tab and assert each selector receives focus in sequence."""
    assert selectors, "Focus order selectors cannot be empty."
    for selector in selectors:
        tab_to_next(page)
        assert_focused(page, selector)


def get_active_element_text(page: Any) -> str:
    return page.evaluate(
        """() => {
            const element = document.activeElement;
            if (!element) return "";
            return element.innerText || element.value || element.getAttribute("aria-label") || "";
        }"""
    )


def assert_active_element_text(
    page: Any,
    expected_text: str,
    *,
    contains: bool = True,
) -> None:
    actual_text = get_active_element_text(page)
    if contains:
        assert expected_text in actual_text, (
            f"Expected active element text to contain {expected_text!r}, got {actual_text!r}"
        )
        return
    assert actual_text == expected_text, (
        f"Expected active element text to be {expected_text!r}, got {actual_text!r}"
    )


def _validate_positive_times(times: int) -> None:
    assert times >= 1, f"Expected times to be >= 1, got {times}"
