from __future__ import annotations

from pathlib import Path
from typing import Any

from utils.helpers.allure_debug import attach_file
from utils.helpers.files import assert_file_exists


def capture_page_screenshot(
    page: Any,
    path: Path | str,
    *,
    full_page: bool = True,
    mask: list[Any] | None = None,
    attach_to_allure: bool = False,
    attachment_name: str | None = None,
) -> Path:
    screenshot_path = _prepare_output_path(path)
    page.screenshot(
        path=str(screenshot_path),
        full_page=full_page,
        mask=mask or None,
    )
    if attach_to_allure:
        attach_file(screenshot_path, name=attachment_name or screenshot_path.name)
    return screenshot_path


def capture_element_screenshot(
    locator: Any,
    path: Path | str,
    *,
    mask: list[Any] | None = None,
    attach_to_allure: bool = False,
    attachment_name: str | None = None,
) -> Path:
    screenshot_path = _prepare_output_path(path)
    locator.screenshot(path=str(screenshot_path), mask=mask or None)
    if attach_to_allure:
        attach_file(screenshot_path, name=attachment_name or screenshot_path.name)
    return screenshot_path


def assert_screenshot_matches_baseline(
    actual_path: Path | str,
    baseline_path: Path | str,
    *,
    update_baseline: bool = False,
) -> Path:
    actual = assert_file_exists(actual_path)
    baseline = Path(baseline_path)

    if update_baseline or not baseline.exists():
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_bytes(actual.read_bytes())
        return baseline

    assert baseline.is_file(), f"Expected baseline path to be a file: {baseline}"
    assert actual.read_bytes() == baseline.read_bytes(), (
        f"Screenshot does not match baseline.\nActual: {actual}\nBaseline: {baseline}"
    )
    return baseline


def assert_screenshot_created(path: Path | str) -> Path:
    file_path = assert_file_exists(path)
    assert file_path.stat().st_size > 0, f"Expected screenshot to be non-empty: {file_path}"
    return file_path


def screenshot_path(
    directory: Path | str,
    name: str,
    *,
    extension: str = ".png",
) -> Path:
    normalized_extension = extension if extension.startswith(".") else f".{extension}"
    safe_name = "".join(character if character.isalnum() or character in "-_." else "_" for character in name)
    return Path(directory) / f"{safe_name}{normalized_extension}"


def _prepare_output_path(path: Path | str) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path
