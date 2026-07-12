import pytest

from utils.helpers.file_transfer import (
    assert_download_extension,
    assert_download_filename,
    assert_file_contains,
    assert_upload_file_ready,
    create_upload_file,
    save_download,
    set_input_files,
    wait_for_download,
)


pytestmark = pytest.mark.helpers


class FakeDownload:
    def __init__(self, suggested_filename="report.csv", content="id,name\n1,qa"):
        self.suggested_filename = suggested_filename
        self.content = content
        self.saved_path = None

    def save_as(self, path):
        self.saved_path = path
        with open(path, "w", encoding="utf-8") as file:
            file.write(self.content)


class FakeDownloadContext:
    def __init__(self, download):
        self.value = download

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakePage:
    def __init__(self, download=None):
        self.download = download or FakeDownload()
        self.uploads = []

    def expect_download(self, timeout):
        assert timeout == 5000
        return FakeDownloadContext(self.download)

    def set_input_files(self, selector, path):
        self.uploads.append((selector, path))


class FakeLocator:
    def __init__(self):
        self.uploads = []

    def set_input_files(self, path):
        self.uploads.append(path)


def test_save_download_uses_suggested_filename(tmp_path):
    download = FakeDownload(suggested_filename="users.csv")

    path = save_download(download, downloads_dir=tmp_path)

    assert path == tmp_path / "users.csv"
    assert path.read_text(encoding="utf-8") == "id,name\n1,qa"


def test_wait_for_download_runs_trigger_and_saves_file(tmp_path):
    page = FakePage()
    triggered = {"value": False}

    path = wait_for_download(
        page,
        lambda: triggered.update(value=True),
        downloads_dir=tmp_path,
        timeout_ms=5000,
    )

    assert triggered["value"] is True
    assert path.name == "report.csv"
    assert path.exists()


def test_download_assertions_validate_filename_extension_and_content(tmp_path):
    file_path = tmp_path / "orders.csv"
    file_path.write_text("order_id,total\n1,29.99", encoding="utf-8")

    assert_download_filename(file_path, "orders.csv")
    assert_download_filename(file_path, "orders", contains=True)
    assert_download_extension(file_path, ".csv")
    assert_file_contains(file_path, "29.99")


def test_create_upload_file_and_validate_size(tmp_path):
    upload_path = create_upload_file(
        tmp_path,
        "avatar.txt",
        content="fake image bytes",
    )

    assert upload_path.exists()
    assert_upload_file_ready(upload_path, max_size_bytes=100)


def test_assert_upload_file_ready_fails_for_large_file(tmp_path):
    upload_path = create_upload_file(tmp_path, "large.txt", content="123456")

    with pytest.raises(AssertionError, match="at most 3 bytes"):
        assert_upload_file_ready(upload_path, max_size_bytes=3)


def test_set_input_files_supports_page_selector(tmp_path):
    page = FakePage()
    upload_path = create_upload_file(tmp_path, "document.txt", content="hello")

    result = set_input_files(page, "input[type=file]", upload_path)

    assert result == upload_path
    assert page.uploads == [("input[type=file]", str(upload_path))]


def test_set_input_files_supports_locator(tmp_path):
    locator = FakeLocator()
    upload_path = create_upload_file(tmp_path, "document.txt", content="hello")

    result = set_input_files(locator, upload_path)

    assert result == upload_path
    assert locator.uploads == [str(upload_path)]
