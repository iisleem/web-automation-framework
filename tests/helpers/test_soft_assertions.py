import pytest

from utils.helpers.soft_assertions import SoftAssert, soft_assert


pytestmark = pytest.mark.helpers


def test_soft_assert_collects_multiple_failures():
    softly = SoftAssert()

    softly.assert_equal("actual", "expected", "Name mismatch")
    softly.assert_true(False, "User should be active")
    softly.assert_contains("checkout error", "success")

    assert softly.has_failures is True
    assert len(softly.failures) == 3

    with pytest.raises(AssertionError, match="Soft assertion failures \\(3\\)"):
        softly.assert_all()


def test_soft_assert_passes_when_no_failures_exist():
    softly = SoftAssert()

    softly.assert_equal("expected", "expected")
    softly.assert_true(True, "User should be active")
    softly.assert_contains("checkout success", "success")
    softly.assert_in("admin", ["admin", "qa"])

    softly.assert_all()


def test_soft_assert_check_captures_assertion_errors():
    softly = soft_assert()

    softly.check("Verify total", lambda: assert_total())

    assert softly.has_failures is True
    assert softly.failures[0].description == "Verify total"
    assert "total mismatch" in softly.failures[0].message


def test_soft_assert_check_does_not_capture_successful_assertions():
    softly = soft_assert()

    softly.check("Verify total", lambda: None)

    assert softly.has_failures is False


def test_soft_assert_format_failures_is_readable():
    softly = SoftAssert()
    softly.assert_in("missing", ["available"])

    message = softly.format_failures()

    assert "Soft assertion failures (1)" in message
    assert "Expected 'missing' to exist" in message


def assert_total():
    assert 10 == 12, "total mismatch"
