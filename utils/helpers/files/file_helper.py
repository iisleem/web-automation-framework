from __future__ import annotations

from pathlib import Path

from automation_core.helpers.files import (
    assert_file_exists as assert_file_exists,
    assert_file_extension as assert_file_extension,
    cleanup_directory as core_cleanup_directory,
    wait_for_file as wait_for_file,
)


def cleanup_directory(path: Path | str) -> None:
    core_cleanup_directory(path, recreate=True)
