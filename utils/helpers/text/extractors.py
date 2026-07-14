from __future__ import annotations

from automation_core.helpers.text import (
    extract_first_match as extract_first_match,
    extract_numbers as core_extract_numbers,
    extract_otp as extract_otp,
    normalize_text as normalize_text,
)


DEFAULT_OTP_REGEX = r"\b\d{4,8}\b"


def extract_numbers(text: str) -> list[str]:
    return core_extract_numbers(text, allow_decimal=False)
