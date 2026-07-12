from collections.abc import Sequence
from typing import Any

import allure


def assert_equal(actual: Any, expected: Any, message: str = "") -> None:
    with allure.step(message or f"Verify '{actual}' equals '{expected}'"):
        assert actual == expected, message or f"Expected {expected!r}, got {actual!r}"


def assert_true(condition: bool, message: str) -> None:
    with allure.step(message):
        assert condition, message


def assert_contains(actual: str, expected_substring: str, message: str = "") -> None:
    with allure.step(message or f"Verify text contains '{expected_substring}'"):
        assert expected_substring in actual, (
            message or f"Expected {actual!r} to contain {expected_substring!r}"
        )


def assert_list_sorted(
    actual: Sequence[Any],
    reverse: bool = False,
    message: str = "",
) -> None:
    expected = sorted(actual, reverse=reverse)
    direction = "descending" if reverse else "ascending"
    with allure.step(message or f"Verify list is sorted {direction}"):
        assert list(actual) == expected, (
            message or f"Expected {list(actual)!r} to be sorted {direction}"
        )
