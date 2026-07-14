from __future__ import annotations

from typing import Any, Literal


TextMatchMode = Literal["exact", "contains"]


def assert_page_title(
    page: Any,
    expected_title: str,
    *,
    mode: TextMatchMode = "exact",
) -> str:
    actual_title = page.title()
    _assert_text(actual_title, expected_title, mode, "page title")
    return actual_title


def assert_html_lang(page: Any, expected_lang: str | None = None) -> str:
    lang = page.locator("html").get_attribute("lang")
    assert lang, "Expected html element to have a non-empty lang attribute"
    if expected_lang is not None:
        assert lang == expected_lang, f"Expected html lang {expected_lang!r}, got {lang!r}"
    return lang


def assert_heading_visible(
    page: Any,
    heading_text: str,
    *,
    level: int | None = None,
    mode: TextMatchMode = "exact",
) -> Any:
    locator = (
        page.get_by_role("heading", name=heading_text, level=level)
        if level is not None
        else page.get_by_role("heading", name=heading_text)
    )
    assert locator.is_visible(), f"Expected heading {heading_text!r} to be visible"
    if mode == "contains":
        actual_text = locator.inner_text()
        assert heading_text in actual_text, f"Expected heading text to contain {heading_text!r}, got {actual_text!r}"
    return locator


def assert_images_have_alt_text(page: Any, selector: str = "img") -> None:
    images = page.locator(selector)
    missing: list[str] = []
    for index in range(images.count()):
        image = images.nth(index)
        alt_text = image.get_attribute("alt")
        if not alt_text:
            src = image.get_attribute("src") or f"{selector}[{index}]"
            missing.append(src)
    assert not missing, "Expected all images to have alt text. Missing: " + ", ".join(missing)


def assert_element_accessible_name(
    page: Any,
    role: str,
    name: str,
) -> Any:
    locator = page.get_by_role(role, name=name)
    assert locator.count() > 0, f"Expected {role!r} with accessible name {name!r}"
    return locator


def assert_minimum_heading_count(page: Any, minimum_count: int = 1) -> int:
    headings = page.get_by_role("heading")
    count = headings.count()
    assert count >= minimum_count, f"Expected at least {minimum_count} heading(s), found {count}"
    return count


def _assert_text(
    actual: str,
    expected: str,
    mode: TextMatchMode,
    label: str,
) -> None:
    if mode == "contains":
        assert expected in actual, f"Expected {label} to contain {expected!r}, got {actual!r}"
        return
    assert actual == expected, f"Expected {label} {expected!r}, got {actual!r}"
