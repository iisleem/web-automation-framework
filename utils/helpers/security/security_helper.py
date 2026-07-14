from __future__ import annotations

import fnmatch
from typing import Any

from automation_core.helpers.security import (
    assert_cookie_security_flags as assert_cookie_security_flags,
    assert_header_present as assert_header_present,
    assert_no_sensitive_values_in_json as assert_no_sensitive_values_in_json,
    assert_no_sensitive_values_in_text as assert_no_sensitive_values_in_text,
    assert_security_headers as assert_security_headers,
    get_response_headers as get_response_headers,
)

DEFAULT_SECURITY_HEADERS = {
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
}

SENSITIVE_VALUE_PATTERNS = (
    "*password*",
    "*secret*",
    "*token*",
    "*api_key*",
    "*apikey*",
    "*authorization*",
)


def assert_no_sensitive_values_in_storage(
    page: Any,
    patterns: tuple[str, ...] = SENSITIVE_VALUE_PATTERNS,
) -> None:
    storage_snapshot = page.evaluate(
        """() => JSON.stringify({
            localStorage: {...localStorage},
            sessionStorage: {...sessionStorage}
        })"""
    )
    lowered_snapshot = str(storage_snapshot).lower()
    matches = [pattern for pattern in patterns if fnmatch.fnmatch(lowered_snapshot, pattern)]
    assert not matches, f"Sensitive value patterns found in browser storage: {matches!r}"
