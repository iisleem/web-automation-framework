from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from utils.helpers.browser import read_storage_state, save_storage_state


def storage_state_exists(path: Path | str) -> bool:
    state_path = Path(path)
    return state_path.exists() and state_path.is_file() and state_path.stat().st_size > 0


def create_authenticated_state(
    page: Any,
    path: Path | str,
    login_action: Callable[[Any], None],
    *,
    verify_action: Callable[[Any], None] | None = None,
) -> Path:
    """Run a login workflow and save the resulting Playwright storage state."""
    login_action(page)
    if verify_action is not None:
        verify_action(page)
    return save_storage_state(page, path)


def new_context_with_storage(
    browser: Any,
    path: Path | str,
    **context_options: Any,
) -> Any:
    state_path = Path(path)
    assert storage_state_exists(state_path), f"Storage state file does not exist: {state_path}"
    return browser.new_context(storage_state=str(state_path), **context_options)


def clear_auth_state(path: Path | str) -> None:
    state_path = Path(path)
    if state_path.exists():
        state_path.unlink()


def assert_storage_state_has_cookies(
    path: Path | str,
    cookie_names: list[str] | None = None,
) -> dict[str, Any]:
    state = read_storage_state(path)
    cookies = state.get("cookies", [])
    assert cookies, f"Expected storage state {path!s} to contain cookies."

    if cookie_names:
        available_names = {cookie.get("name") for cookie in cookies}
        missing_names = [name for name in cookie_names if name not in available_names]
        assert not missing_names, (
            f"Expected storage state {path!s} to contain cookies {missing_names!r}. "
            f"Available cookies: {sorted(available_names)!r}"
        )

    return state


def assert_storage_state_has_origin(path: Path | str, origin: str) -> dict[str, Any]:
    state = read_storage_state(path)
    origins = {entry.get("origin") for entry in state.get("origins", [])}
    assert origin in origins, (
        f"Expected storage state {path!s} to contain origin {origin!r}. "
        f"Available origins: {sorted(origins)!r}"
    )
    return state
