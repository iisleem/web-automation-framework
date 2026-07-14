from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader

from utils.helpers.files import assert_file_exists


def get_pdf_page_count(path: Path | str, *, password: str | None = None) -> int:
    reader = _reader(path, password=password)
    return len(reader.pages)


def read_pdf_text(path: Path | str, *, password: str | None = None) -> str:
    reader = _reader(path, password=password)
    page_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(page_text)


def get_pdf_metadata(path: Path | str, *, password: str | None = None) -> dict[str, Any]:
    reader = _reader(path, password=password)
    metadata = reader.metadata or {}
    return {str(key).lstrip("/"): value for key, value in dict(metadata).items()}


def assert_pdf_page_count(
    path: Path | str,
    expected_count: int,
    *,
    password: str | None = None,
) -> None:
    actual_count = get_pdf_page_count(path, password=password)
    assert actual_count == expected_count, f"Expected PDF {path!s} to have {expected_count} pages, got {actual_count}"


def assert_pdf_contains_text(
    path: Path | str,
    expected_text: str,
    *,
    password: str | None = None,
) -> None:
    actual_text = read_pdf_text(path, password=password)
    assert expected_text in actual_text, f"Expected PDF {path!s} to contain {expected_text!r}."


def assert_pdf_metadata_contains(
    path: Path | str,
    key: str,
    expected_value: str,
    *,
    password: str | None = None,
) -> None:
    metadata = get_pdf_metadata(path, password=password)
    actual_value = metadata.get(key)
    assert (
        actual_value == expected_value
    ), f"Expected PDF metadata {key!r} to be {expected_value!r}, got {actual_value!r}"


def _reader(path: Path | str, *, password: str | None = None) -> PdfReader:
    file_path = assert_file_exists(path)
    reader = PdfReader(str(file_path))
    if reader.is_encrypted and password:
        reader.decrypt(password)
    return reader
