import pytest
from pypdf import PdfWriter

from utils.helpers.pdf import (
    assert_pdf_contains_text,
    assert_pdf_metadata_contains,
    assert_pdf_page_count,
    get_pdf_metadata,
    get_pdf_page_count,
    read_pdf_text,
)


pytestmark = pytest.mark.helpers


def test_pdf_page_count_and_metadata_helpers(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata({"/Title": "Automation Report"})
    with pdf_path.open("wb") as file:
        writer.write(file)

    assert get_pdf_page_count(pdf_path) == 2
    assert get_pdf_metadata(pdf_path)["Title"] == "Automation Report"
    assert_pdf_page_count(pdf_path, 2)
    assert_pdf_metadata_contains(pdf_path, "Title", "Automation Report")


def test_pdf_text_assertion_uses_extracted_text(monkeypatch, tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with pdf_path.open("wb") as file:
        writer.write(file)

    class FakePage:
        def extract_text(self):
            return "Invoice total is 42 JOD"

    class FakeReader:
        is_encrypted = False
        pages = [FakePage()]
        metadata = {}

    monkeypatch.setattr("utils.helpers.pdf.pdf_helper.PdfReader", lambda path: FakeReader())

    assert read_pdf_text(pdf_path) == "Invoice total is 42 JOD"
    assert_pdf_contains_text(pdf_path, "42 JOD")


def test_pdf_assertions_have_clear_failure_messages(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with pdf_path.open("wb") as file:
        writer.write(file)

    with pytest.raises(AssertionError, match="to have 2 pages"):
        assert_pdf_page_count(pdf_path, 2)

    with pytest.raises(AssertionError, match="to contain"):
        assert_pdf_contains_text(pdf_path, "missing text")
