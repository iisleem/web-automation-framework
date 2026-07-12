from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_storage_state(context_or_page: Any, path: Path | str) -> Path:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    context = _context_from(context_or_page)
    context.storage_state(path=str(state_path))
    return state_path


def read_storage_state(path: Path | str) -> dict[str, Any]:
    state_path = Path(path)
    with state_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def clear_browser_storage(page: Any) -> None:
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    page.context.clear_cookies()


def set_local_storage_item(page: Any, key: str, value: str) -> None:
    page.evaluate(
        "([key, value]) => localStorage.setItem(key, value)",
        [key, value],
    )


def get_local_storage_item(page: Any, key: str) -> str | None:
    return page.evaluate("(key) => localStorage.getItem(key)", key)


def _context_from(context_or_page: Any) -> Any:
    return getattr(context_or_page, "context", context_or_page)
