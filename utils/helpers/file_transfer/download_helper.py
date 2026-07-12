from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from utils.helpers.files import assert_file_extension, assert_file_exists


def wait_for_download(
    page: Any,
    trigger: Callable[[], Any],
    *,
    downloads_dir: Path | str,
    filename: str | None = None,
    timeout_ms: int = 30000,
) -> Path:
    with page.expect_download(timeout=timeout_ms) as download_info:
        trigger()

    return save_download(
        download_info.value,
        downloads_dir=downloads_dir,
        filename=filename,
    )


def save_download(
    download: Any,
    *,
    downloads_dir: Path | str,
    filename: str | None = None,
) -> Path:
    output_dir = Path(downloads_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_filename = filename or download.suggested_filename
    output_path = output_dir / resolved_filename
    download.save_as(str(output_path))
    return output_path


def assert_download_filename(
    path: Path | str,
    expected_filename: str,
    *,
    contains: bool = False,
) -> Path:
    file_path = assert_file_exists(path)
    if contains:
        assert expected_filename in file_path.name, (
            f"Expected downloaded filename to contain {expected_filename!r}, got {file_path.name!r}"
        )
    else:
        assert file_path.name == expected_filename, (
            f"Expected downloaded filename {expected_filename!r}, got {file_path.name!r}"
        )
    return file_path


def assert_download_extension(path: Path | str, expected_extension: str) -> Path:
    return assert_file_extension(path, expected_extension)


def assert_file_contains(
    path: Path | str,
    expected_text: str,
    *,
    encoding: str = "utf-8",
) -> Path:
    file_path = assert_file_exists(path)
    content = file_path.read_text(encoding=encoding)
    assert expected_text in content, (
        f"Expected file {file_path} to contain {expected_text!r}"
    )
    return file_path
