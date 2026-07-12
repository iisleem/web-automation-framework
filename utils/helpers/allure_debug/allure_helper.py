from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import json
from pathlib import Path
from typing import Any

import allure


@contextmanager
def step(title: str) -> Iterator[None]:
    with allure.step(title):
        yield


def attach_text(
    content: str,
    name: str = "text attachment",
    *,
    allure_api: Any = allure,
) -> None:
    allure_api.attach(
        content,
        name=name,
        attachment_type=allure_api.attachment_type.TEXT,
    )


def attach_json(
    data: Any,
    name: str = "json attachment",
    *,
    indent: int = 2,
    allure_api: Any = allure,
) -> None:
    allure_api.attach(
        json.dumps(data, indent=indent, ensure_ascii=False),
        name=name,
        attachment_type=allure_api.attachment_type.JSON,
    )


def attach_file(
    path: Path | str,
    name: str | None = None,
    *,
    attachment_type: Any | None = None,
    extension: str | None = None,
    allure_api: Any = allure,
) -> Path:
    file_path = Path(path)
    assert file_path.exists(), f"Attachment file does not exist: {file_path}"
    assert file_path.is_file(), f"Attachment path is not a file: {file_path}"

    allure_api.attach.file(
        str(file_path),
        name=name or file_path.name,
        attachment_type=attachment_type,
        extension=extension,
    )
    return file_path


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
