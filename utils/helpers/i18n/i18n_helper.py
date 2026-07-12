from __future__ import annotations

from typing import Any, Literal


Direction = Literal["ltr", "rtl"]


RTL_LANGUAGES = {"ar", "fa", "he", "ur"}


def normalize_locale(locale: str) -> str:
    return locale.replace("_", "-").strip().lower()


def expected_direction_for_locale(locale: str) -> Direction:
    language = normalize_locale(locale).split("-")[0]
    return "rtl" if language in RTL_LANGUAGES else "ltr"


def assert_page_locale(page: Any, expected_locale: str) -> None:
    actual_locale = page.locator("html").get_attribute("lang")
    assert normalize_locale(actual_locale or "") == normalize_locale(expected_locale), (
        f"Expected page locale {expected_locale!r}, got {actual_locale!r}"
    )


def assert_page_direction(page: Any, expected_direction: Direction) -> None:
    actual_direction = page.locator("html").get_attribute("dir") or page.evaluate(
        "() => getComputedStyle(document.documentElement).direction"
    )
    assert actual_direction == expected_direction, (
        f"Expected page direction {expected_direction!r}, got {actual_direction!r}"
    )


def assert_locale_direction(page: Any, locale: str) -> None:
    assert_page_locale(page, locale)
    assert_page_direction(page, expected_direction_for_locale(locale))


def assert_no_untranslated_keys(
    page: Any,
    *,
    key_prefixes: tuple[str, ...] = ("i18n.", "translation.", "common."),
) -> None:
    body_text = page.locator("body").inner_text()
    leaked_keys = [prefix for prefix in key_prefixes if prefix in body_text]
    assert not leaked_keys, f"Untranslated i18n keys appear on the page: {leaked_keys!r}"


def switch_language(
    page: Any,
    selector: str,
    locale: str,
    *,
    wait_for_locale: bool = True,
) -> None:
    page.locator(selector).select_option(locale)
    if wait_for_locale:
        assert_page_locale(page, locale)
