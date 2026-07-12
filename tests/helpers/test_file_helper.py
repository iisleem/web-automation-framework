from pathlib import Path

import pytest

from utils.helpers.files import (
    assert_file_exists,
    assert_file_extension,
    cleanup_directory,
    wait_for_file,
)


pytestmark = pytest.mark.helpers


def test_wait_for_file_returns_matching_file(tmp_path):
    file_path = tmp_path / "report.csv"
    file_path.write_text("id,name\n1,qa", encoding="utf-8")

    result = wait_for_file(
        tmp_path,
        pattern="*.csv",
        timeout_seconds=1,
        interval_seconds=0.01,
    )

    assert result == file_path


def test_assert_file_exists_returns_path(tmp_path):
    file_path = tmp_path / "download.txt"
    file_path.write_text("content", encoding="utf-8")

    assert assert_file_exists(file_path) == file_path


def test_assert_file_extension_accepts_extension_without_dot(tmp_path):
    file_path = tmp_path / "download.pdf"
    file_path.write_text("content", encoding="utf-8")

    assert assert_file_extension(file_path, "pdf") == file_path


def test_assert_file_exists_fails_for_missing_file(tmp_path):
    with pytest.raises(AssertionError, match="Expected file to exist"):
        assert_file_exists(tmp_path / "missing.txt")


def test_cleanup_directory_recreates_empty_directory(tmp_path):
    directory = tmp_path / "downloads"
    directory.mkdir()
    (directory / "old.txt").write_text("old", encoding="utf-8")

    cleanup_directory(directory)

    assert directory.exists()
    assert list(directory.iterdir()) == []
