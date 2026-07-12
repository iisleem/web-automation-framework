from datetime import date, datetime, timezone

import pytest

from utils.helpers.date_time import (
    add_days,
    format_date,
    parse_date,
    today,
    tomorrow,
    utc_now,
    yesterday,
)


pytestmark = pytest.mark.helpers


def test_utc_now_returns_timezone_aware_datetime():
    value = utc_now()

    assert isinstance(value, datetime)
    assert value.tzinfo == timezone.utc


def test_today_tomorrow_and_yesterday_are_relative_dates():
    current = today("UTC")

    assert tomorrow("UTC") == add_days(current, 1)
    assert yesterday("UTC") == add_days(current, -1)


def test_add_days_returns_shifted_date():
    assert add_days(date(2026, 5, 16), 3) == date(2026, 5, 19)


def test_format_and_parse_date():
    value = date(2026, 5, 16)

    assert format_date(value) == "2026-05-16"
    assert parse_date("16/05/2026", "%d/%m/%Y") == value
