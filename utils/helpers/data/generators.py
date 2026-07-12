from __future__ import annotations

from datetime import datetime, timezone
import random
import string
import uuid


def unique_id(prefix: str = "auto") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def timestamped_value(prefix: str = "auto") -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}-{timestamp}"


def random_email(
    domain: str = "example.com",
    prefix: str = "automation",
) -> str:
    return f"{prefix}.{uuid.uuid4().hex[:10]}@{domain}"


def random_username(prefix: str = "user", length: int = 8) -> str:
    suffix = _random_alphanumeric(length)
    return f"{prefix}_{suffix}"


def random_phone(country_code: str = "+1", digits: int = 10) -> str:
    number = "".join(random.choices(string.digits, k=digits))
    return f"{country_code}{number}"


def _random_alphanumeric(length: int) -> str:
    if length < 1:
        raise ValueError("length must be at least 1")
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))
