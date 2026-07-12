import pytest

from utils.helpers.text import (
    extract_first_match,
    extract_numbers,
    extract_otp,
    normalize_text,
)


pytestmark = pytest.mark.helpers


def test_normalize_text_collapses_whitespace():
    assert normalize_text("Hello   automation\nteam") == "Hello automation team"


def test_extract_otp_returns_first_otp_like_value():
    assert extract_otp("Your verification code is 482913.") == "482913"


def test_extract_otp_accepts_custom_regex():
    assert extract_otp("Code: AB-4829", regex=r"AB-\d{4}") == "AB-4829"


def test_extract_first_match_returns_first_capture_group_when_present():
    result = extract_first_match("Order ID: ORD-12345", r"Order ID: ([A-Z]+-\d+)")

    assert result == "ORD-12345"


def test_extract_first_match_returns_none_when_no_match():
    assert extract_first_match("No order here", r"Order ID: ([A-Z]+-\d+)") is None


def test_extract_numbers_returns_all_numeric_groups():
    assert extract_numbers("Total: $42. Tax: $3") == ["42", "3"]
