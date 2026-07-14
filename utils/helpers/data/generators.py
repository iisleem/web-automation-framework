from __future__ import annotations

from automation_core.helpers.data import (
    random_email as core_random_email,
    random_phone as random_phone,
    random_string as random_string,
    random_username as random_username,
    timestamped_value as core_timestamped_value,
    unique_id as core_unique_id,
)


def unique_id(prefix: str = "auto") -> str:
    return core_unique_id(prefix=prefix, length=10)


def timestamped_value(prefix: str = "auto") -> str:
    return core_timestamped_value(prefix=prefix, timestamp_format="%Y%m%d%H%M%S%f")


def random_email(
    domain: str = "example.com",
    prefix: str = "automation",
) -> str:
    return core_random_email(domain=domain, prefix=prefix)
