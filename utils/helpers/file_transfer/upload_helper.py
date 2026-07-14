from __future__ import annotations

from pathlib import Path
from typing import Any

from utils.helpers.files import assert_file_exists


def create_upload_file(
    directory: Path | str,
    filename: str,
    content: str = "",
    *,
    encoding: str = "utf-8",
) -> Path:
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / filename
    file_path.write_text(content, encoding=encoding)
    return file_path


def set_input_files(
    page_or_locator: Any,
    selector_or_path: str | Path,
    file_path: str | Path | None = None,
) -> Path:
    if file_path is None:
        locator = page_or_locator
        upload_path = assert_file_exists(selector_or_path)
        locator.set_input_files(str(upload_path))
        return upload_path

    page = page_or_locator
    upload_path = assert_file_exists(file_path)
    page.set_input_files(str(selector_or_path), str(upload_path))
    return upload_path


def assert_upload_file_ready(
    path: Path | str,
    *,
    max_size_bytes: int | None = None,
) -> Path:
    file_path = assert_file_exists(path)
    if max_size_bytes is not None:
        size = file_path.stat().st_size
        assert (
            size <= max_size_bytes
        ), f"Expected upload file {file_path} to be at most {max_size_bytes} bytes, got {size}"
    return file_path
