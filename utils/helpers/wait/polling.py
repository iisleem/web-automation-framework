from __future__ import annotations

from collections.abc import Callable
import time
from typing import TypeVar


T = TypeVar("T")


def wait_until(
    condition: Callable[[], T | None | bool],
    timeout_seconds: float = 30,
    interval_seconds: float = 1,
    failure_message: str = "Condition was not met before timeout.",
) -> T:
    deadline = time.monotonic() + timeout_seconds
    last_value = None

    while time.monotonic() <= deadline:
        last_value = condition()
        if last_value:
            return last_value
        time.sleep(interval_seconds)

    raise TimeoutError(f"{failure_message} Last value: {last_value!r}")
