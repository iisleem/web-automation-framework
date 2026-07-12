from __future__ import annotations

from typing import Any


def get_cookies(context_or_page: Any) -> list[dict[str, Any]]:
    return _context_from(context_or_page).cookies()


def get_cookie(context_or_page: Any, name: str) -> dict[str, Any] | None:
    return next(
        (cookie for cookie in get_cookies(context_or_page) if cookie.get("name") == name),
        None,
    )


def assert_cookie_exists(context_or_page: Any, name: str) -> dict[str, Any]:
    cookie = get_cookie(context_or_page, name)
    assert cookie is not None, f"Expected cookie {name!r} to exist"
    return cookie


def assert_cookie_value(
    context_or_page: Any,
    name: str,
    expected_value: str,
) -> dict[str, Any]:
    cookie = assert_cookie_exists(context_or_page, name)
    actual_value = cookie.get("value")
    assert actual_value == expected_value, (
        f"Expected cookie {name!r} value {expected_value!r}, got {actual_value!r}"
    )
    return cookie


def assert_cookie_attribute(
    context_or_page: Any,
    name: str,
    attribute: str,
    expected_value: Any,
) -> dict[str, Any]:
    cookie = assert_cookie_exists(context_or_page, name)
    actual_value = cookie.get(attribute)
    assert actual_value == expected_value, (
        f"Expected cookie {name!r} attribute {attribute!r} to be {expected_value!r}, "
        f"got {actual_value!r}"
    )
    return cookie


def set_cookie(
    context_or_page: Any,
    *,
    name: str,
    value: str,
    domain: str | None = None,
    path: str = "/",
    url: str | None = None,
    expires: int | None = None,
    http_only: bool = False,
    secure: bool = False,
    same_site: str = "Lax",
) -> dict[str, Any]:
    cookie = {
        "name": name,
        "value": value,
        "path": path,
        "httpOnly": http_only,
        "secure": secure,
        "sameSite": same_site,
    }
    if url:
        cookie["url"] = url
    if domain:
        cookie["domain"] = domain
    if expires is not None:
        cookie["expires"] = expires

    _context_from(context_or_page).add_cookies([cookie])
    return cookie


def delete_cookie(
    context_or_page: Any,
    name: str,
    *,
    domain: str | None = None,
    path: str | None = None,
) -> None:
    clear_kwargs: dict[str, str] = {"name": name}
    if domain:
        clear_kwargs["domain"] = domain
    if path:
        clear_kwargs["path"] = path
    _context_from(context_or_page).clear_cookies(**clear_kwargs)


def copy_cookies(source_context_or_page: Any, target_context_or_page: Any) -> list[dict[str, Any]]:
    cookies = get_cookies(source_context_or_page)
    _context_from(target_context_or_page).add_cookies(cookies)
    return cookies


def _context_from(context_or_page: Any) -> Any:
    return getattr(context_or_page, "context", context_or_page)
