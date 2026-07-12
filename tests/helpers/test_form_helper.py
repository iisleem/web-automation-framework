import pytest

from utils.helpers.forms import (
    FormField,
    assert_checkbox_checked,
    assert_field_value,
    assert_validation_message,
    clear_fields,
    fill_form,
    submit_and_wait_for_url,
)


pytestmark = pytest.mark.helpers


class FakeLocator:
    def __init__(self, selector):
        self.selector = selector
        self.value = ""
        self.checked = False
        self.selected = None
        self.files = None
        self.clicked = False
        self.text = ""

    def fill(self, value):
        self.value = value

    def set_checked(self, value):
        self.checked = value

    def select_option(self, value):
        self.selected = value

    def set_input_files(self, path):
        self.files = path

    def input_value(self):
        return self.value

    def is_checked(self):
        return self.checked

    def inner_text(self):
        return self.text

    def click(self):
        self.clicked = True


class FakePage:
    def __init__(self):
        self.locators = {}
        self.waits = []

    def locator(self, selector):
        if selector not in self.locators:
            self.locators[selector] = FakeLocator(selector)
        return self.locators[selector]

    def wait_for_url(self, pattern, timeout):
        self.waits.append((pattern, timeout))


def test_fill_form_accepts_simple_field_map():
    page = FakePage()

    fill_form(
        page,
        {
            "[data-test='first-name']": "Alex",
            "[data-test='last-name']": "Tester",
        },
    )

    assert page.locator("[data-test='first-name']").value == "Alex"
    assert page.locator("[data-test='last-name']").value == "Tester"


def test_fill_form_supports_checkbox_select_and_file_fields(tmp_path):
    page = FakePage()
    upload_path = tmp_path / "document.txt"

    fill_form(
        page,
        [
            FormField("#terms", True, "checkbox"),
            FormField("#country", "JO", "select"),
            FormField("#document", upload_path, "file"),
        ],
    )

    assert page.locator("#terms").checked is True
    assert page.locator("#country").selected == "JO"
    assert page.locator("#document").files == str(upload_path)


def test_clear_fields_clears_text_inputs():
    page = FakePage()
    page.locator("#first").value = "Alex"
    page.locator("#last").value = "Tester"

    clear_fields(page, ["#first", "#last"])

    assert page.locator("#first").value == ""
    assert page.locator("#last").value == ""


def test_field_assertions_pass_for_expected_values():
    page = FakePage()
    page.locator("#first").value = "Alex"
    page.locator("#terms").checked = True

    assert_field_value(page, "#first", "Alex")
    assert_checkbox_checked(page, "#terms")


def test_assert_validation_message_supports_contains_and_exact():
    page = FakePage()
    page.locator("#error").text = "First name is required"

    assert_validation_message(page, "#error", "First name")
    assert_validation_message(
        page,
        "#error",
        "First name is required",
        contains=False,
    )


def test_submit_and_wait_for_url_clicks_and_waits():
    page = FakePage()

    submit_and_wait_for_url(page, "#submit", "/complete", timeout_ms=3000)

    assert page.locator("#submit").clicked is True
    assert page.waits == [("**/complete**", 3000)]


def test_assert_field_value_has_clear_failure_message():
    page = FakePage()
    page.locator("#first").value = "Wrong"

    with pytest.raises(AssertionError, match="Expected field"):
        assert_field_value(page, "#first", "Alex")
