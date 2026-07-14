from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import allure
from automation_core.reporting.allure_debug import (
    attach_file as core_attach_file,
    attach_json as core_attach_json,
    attach_text as core_attach_text,
    step as core_step,
)


@contextmanager
def step(title: str) -> Iterator[None]:
    with core_step(title, allure_api=allure):
        yield


def attach_text(
    content: str,
    name: str = "text attachment",
    *,
    allure_api: Any = allure,
) -> None:
    core_attach_text(content, name=name, allure_api=allure_api)


def attach_json(
    data: Any,
    name: str = "json attachment",
    *,
    indent: int = 2,
    allure_api: Any = allure,
) -> None:
    core_attach_json(data, name=name, indent=indent, allure_api=allure_api)


def attach_file(
    path: Path | str,
    name: str | None = None,
    *,
    attachment_type: Any | None = None,
    extension: str | None = None,
    allure_api: Any = allure,
) -> Path:
    return core_attach_file(
        path,
        name=name,
        attachment_type=attachment_type,
        extension=extension,
        allure_api=allure_api,
    )


def attach_page_url(
    page: Any,
    name: str = "page url",
    *,
    allure_api: Any = allure,
) -> str:
    url = getattr(page, "url", "")
    attach_text(url, name=name, allure_api=allure_api)
    return url


def attach_html_snapshot(
    page: Any,
    name: str = "html snapshot",
    *,
    allure_api: Any = allure,
) -> str:
    html = page.content()
    allure_api.attach(
        html,
        name=name,
        attachment_type=allure_api.attachment_type.HTML,
    )
    return html


def attach_locator_text(
    locator: Any,
    name: str = "locator text",
    *,
    allure_api: Any = allure,
) -> str:
    text = locator.inner_text()
    attach_text(text, name=name, allure_api=allure_api)
    return text


def attach_page_debug_snapshot(
    page: Any,
    *,
    include_html: bool = True,
    allure_api: Any = allure,
) -> dict[str, str]:
    snapshot = {"url": attach_page_url(page, allure_api=allure_api)}
    if include_html:
        snapshot["html"] = attach_html_snapshot(page, allure_api=allure_api)
    return snapshot
