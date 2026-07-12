from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


FieldType = Literal["text", "checkbox", "select", "file"]


@dataclass(frozen=True)
class FormField:
    selector: str
    value: Any
    field_type: FieldType = "text"


def fill_form(
    page: Any,
    fields: dict[str, Any] | list[FormField],
) -> None:
    for field in _normalize_fields(fields):
        fill_field(page, field)


def fill_field(page: Any, field: FormField) -> None:
    locator = page.locator(field.selector)
    if field.field_type == "checkbox":
        locator.set_checked(bool(field.value))
        return
    if field.field_type == "select":
        locator.select_option(field.value)
        return
    if field.field_type == "file":
        locator.set_input_files(str(Path(field.value)))
        return
    locator.fill("" if field.value is None else str(field.value))


def clear_fields(page: Any, selectors: list[str]) -> None:
    for selector in selectors:
        page.locator(selector).fill("")


def assert_field_value(page: Any, selector: str, expected_value: str) -> None:
    actual_value = page.locator(selector).input_value()
    assert actual_value == expected_value, (
        f"Expected field {selector!r} value {expected_value!r}, got {actual_value!r}"
    )


def assert_checkbox_checked(
    page: Any,
    selector: str,
    *,
    expected: bool = True,
) -> None:
    actual = page.locator(selector).is_checked()
    assert actual is expected, (
        f"Expected checkbox {selector!r} checked state {expected}, got {actual}"
    )


def assert_validation_message(
    page: Any,
    selector: str,
    expected_text: str,
    *,
    contains: bool = True,
) -> None:
    actual_text = page.locator(selector).inner_text()
    if contains:
        assert expected_text in actual_text, (
            f"Expected validation message {selector!r} to contain {expected_text!r}, "
            f"got {actual_text!r}"
        )
        return
    assert actual_text == expected_text, (
        f"Expected validation message {selector!r} to be {expected_text!r}, "
        f"got {actual_text!r}"
    )


def submit_and_wait_for_url(
    page: Any,
    submit_selector: str,
    expected_url_part: str,
    *,
    timeout_ms: int = 10000,
) -> None:
    page.locator(submit_selector).click()
    page.wait_for_url(f"**{expected_url_part}**", timeout=timeout_ms)


def _normalize_fields(fields: dict[str, Any] | list[FormField]) -> list[FormField]:
    if isinstance(fields, dict):
        return [FormField(selector=selector, value=value) for selector, value in fields.items()]
    return fields
