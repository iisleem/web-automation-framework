from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SoftAssertionFailure:
    description: str
    message: str


class SoftAssert:
    """Collect assertion failures and fail once with a grouped message."""

    def __init__(self) -> None:
        self.failures: list[SoftAssertionFailure] = []

    @property
    def has_failures(self) -> bool:
        return bool(self.failures)

    def check(self, description: str, assertion: Callable[[], None]) -> None:
        try:
            assertion()
        except AssertionError as error:
            self.failures.append(
                SoftAssertionFailure(
                    description=description,
                    message=str(error) or description,
                )
            )

    def assert_true(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(SoftAssertionFailure(description=message, message=message))

    def assert_equal(self, actual: Any, expected: Any, message: str = "") -> None:
        if actual != expected:
            failure_message = message or f"Expected {expected!r}, got {actual!r}"
            self.failures.append(SoftAssertionFailure(description=failure_message, message=failure_message))

    def assert_contains(self, actual: str, expected_substring: str, message: str = "") -> None:
        if expected_substring not in actual:
            failure_message = message or (f"Expected {actual!r} to contain {expected_substring!r}")
            self.failures.append(SoftAssertionFailure(description=failure_message, message=failure_message))

    def assert_in(self, member: Any, container: Any, message: str = "") -> None:
        if member not in container:
            failure_message = message or f"Expected {member!r} to exist in {container!r}"
            self.failures.append(SoftAssertionFailure(description=failure_message, message=failure_message))

    def assert_all(self) -> None:
        assert not self.failures, self.format_failures()

    def format_failures(self) -> str:
        lines = [f"Soft assertion failures ({len(self.failures)}):"]
        for index, failure in enumerate(self.failures, start=1):
            lines.append(f"{index}. {failure.description}: {failure.message}")
        return "\n".join(lines)


def soft_assert() -> SoftAssert:
    return SoftAssert()
