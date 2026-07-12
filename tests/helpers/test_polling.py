import pytest

from utils.helpers.wait import wait_until


pytestmark = pytest.mark.helpers


def test_wait_until_returns_truthy_value():
    attempts = {"count": 0}

    def condition():
        attempts["count"] += 1
        return "ready" if attempts["count"] == 2 else None

    result = wait_until(
        condition,
        timeout_seconds=1,
        interval_seconds=0.01,
    )

    assert result == "ready"
    assert attempts["count"] == 2


def test_wait_until_raises_timeout_with_context():
    with pytest.raises(TimeoutError, match="Token was not generated"):
        wait_until(
            lambda: None,
            timeout_seconds=0.03,
            interval_seconds=0.01,
            failure_message="Token was not generated",
        )
