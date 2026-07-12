import re

import pytest

from utils.helpers.data import (
    random_email,
    random_phone,
    random_username,
    timestamped_value,
    unique_id,
)


pytestmark = pytest.mark.helpers


def test_unique_id_uses_prefix_and_random_suffix():
    value = unique_id("order")

    assert re.fullmatch(r"order-[a-f0-9]{10}", value)


def test_timestamped_value_uses_prefix():
    value = timestamped_value("run")

    assert value.startswith("run-")
    assert len(value) > len("run-")


def test_random_email_uses_domain_and_prefix():
    email = random_email(domain="example.test", prefix="qa")

    assert re.fullmatch(r"qa\.[a-f0-9]{10}@example\.test", email)


def test_random_username_uses_requested_length():
    username = random_username(prefix="qa", length=6)

    assert re.fullmatch(r"qa_[a-z0-9]{6}", username)


def test_random_phone_uses_country_code_and_digit_count():
    phone = random_phone(country_code="+962", digits=9)

    assert re.fullmatch(r"\+962\d{9}", phone)


def test_random_username_rejects_invalid_length():
    with pytest.raises(ValueError, match="length"):
        random_username(length=0)
