import json

import pytest

from utils.helpers.allure_debug import (
    attach_file,
    attach_html_snapshot,
    attach_json,
    attach_locator_text,
    attach_page_debug_snapshot,
    attach_page_url,
    attach_text,
)


pytestmark = pytest.mark.helpers


class FakeAttachmentType:
    TEXT = "text/plain"
    JSON = "application/json"
    HTML = "text/html"


class FakeAttach:
    def __init__(self) -> None:
        self.calls = []
        self.file_calls = []

    def __call__(self, content, name=None, attachment_type=None, extension=None):
        self.calls.append(
            {
                "content": content,
                "name": name,
                "attachment_type": attachment_type,
                "extension": extension,
            }
        )

    def file(self, path, name=None, attachment_type=None, extension=None):
        self.file_calls.append(
            {
                "path": path,
                "name": name,
                "attachment_type": attachment_type,
                "extension": extension,
            }
        )


class FakeAllure:
    def __init__(self) -> None:
        self.attach = FakeAttach()
        self.attachment_type = FakeAttachmentType()


class FakePage:
    url = "https://example.test/current"

    def content(self):
        return "<html><body>Debug</body></html>"


class FakeLocator:
    def inner_text(self):
        return "Locator text"


def test_attach_text_uses_text_attachment_type():
    fake_allure = FakeAllure()

    attach_text("hello", name="greeting", allure_api=fake_allure)

    assert fake_allure.attach.calls == [
        {
            "content": "hello",
            "name": "greeting",
            "attachment_type": "text/plain",
            "extension": None,
        }
    ]


def test_attach_json_serializes_data():
    fake_allure = FakeAllure()

    attach_json({"name": "Alex"}, name="payload", allure_api=fake_allure)

    call = fake_allure.attach.calls[0]
    assert json.loads(call["content"]) == {"name": "Alex"}
    assert call["attachment_type"] == "application/json"


def test_attach_file_validates_and_attaches_file(tmp_path):
    fake_allure = FakeAllure()
    file_path = tmp_path / "debug.txt"
    file_path.write_text("debug", encoding="utf-8")

    result = attach_file(file_path, allure_api=fake_allure)

    assert result == file_path
    assert fake_allure.attach.file_calls[0]["path"] == str(file_path)
    assert fake_allure.attach.file_calls[0]["name"] == "debug.txt"


def test_attach_file_fails_for_missing_file(tmp_path):
    with pytest.raises(AssertionError, match="Attachment file does not exist"):
        attach_file(tmp_path / "missing.txt")


def test_page_and_locator_debug_attachments():
    fake_allure = FakeAllure()
    page = FakePage()

    assert attach_page_url(page, allure_api=fake_allure) == page.url
    assert attach_html_snapshot(page, allure_api=fake_allure) == page.content()
    assert attach_locator_text(FakeLocator(), allure_api=fake_allure) == "Locator text"

    names = [call["name"] for call in fake_allure.attach.calls]
    assert names == ["page url", "html snapshot", "locator text"]


def test_attach_page_debug_snapshot_returns_url_and_html():
    fake_allure = FakeAllure()

    snapshot = attach_page_debug_snapshot(FakePage(), allure_api=fake_allure)

    assert snapshot == {
        "url": "https://example.test/current",
        "html": "<html><body>Debug</body></html>",
    }
