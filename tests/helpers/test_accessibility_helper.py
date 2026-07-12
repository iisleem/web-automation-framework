import pytest

from utils.helpers.accessibility import (
    assert_element_accessible_name,
    assert_heading_visible,
    assert_html_lang,
    assert_images_have_alt_text,
    assert_minimum_heading_count,
    assert_page_title,
)


pytestmark = pytest.mark.helpers


class FakeLocator:
    def __init__(self, visible=True, text="", attributes=None, children=None):
        self._visible = visible
        self._text = text
        self.attributes = attributes or {}
        self.children = children or []

    def is_visible(self):
        return self._visible

    def inner_text(self):
        return self._text

    def get_attribute(self, name):
        return self.attributes.get(name)

    def count(self):
        return len(self.children) if self.children else 1

    def nth(self, index):
        return self.children[index]


class FakePage:
    def __init__(self):
        self.role_locators = {}
        self.locators = {"html": FakeLocator(attributes={"lang": "en"})}
        self._title = "Automation Dashboard"

    def title(self):
        return self._title

    def locator(self, selector):
        return self.locators[selector]

    def get_by_role(self, role, name=None, level=None):
        return self.role_locators[(role, name, level)]


def test_assert_page_title_supports_exact_and_contains():
    page = FakePage()

    assert_page_title(page, "Automation Dashboard")
    assert_page_title(page, "Dashboard", mode="contains")


def test_assert_html_lang_validates_lang_attribute():
    page = FakePage()

    assert assert_html_lang(page) == "en"
    assert assert_html_lang(page, "en") == "en"


def test_assert_heading_visible_uses_role_and_level():
    page = FakePage()
    heading = FakeLocator(visible=True, text="Welcome to Dashboard")
    page.role_locators[("heading", "Welcome", 1)] = heading

    result = assert_heading_visible(page, "Welcome", level=1, mode="contains")

    assert result == heading


def test_assert_images_have_alt_text_passes_when_all_images_have_alt():
    page = FakePage()
    page.locators["img"] = FakeLocator(
        children=[
            FakeLocator(attributes={"alt": "Logo", "src": "/logo.png"}),
            FakeLocator(attributes={"alt": "Chart", "src": "/chart.png"}),
        ]
    )

    assert_images_have_alt_text(page)


def test_assert_images_have_alt_text_fails_when_image_missing_alt():
    page = FakePage()
    page.locators["img"] = FakeLocator(
        children=[FakeLocator(attributes={"src": "/missing.png"})]
    )

    with pytest.raises(AssertionError, match="/missing.png"):
        assert_images_have_alt_text(page)


def test_assert_element_accessible_name_requires_matching_role():
    page = FakePage()
    button = FakeLocator(children=[FakeLocator()])
    page.role_locators[("button", "Save", None)] = button

    assert assert_element_accessible_name(page, "button", "Save") == button


def test_assert_minimum_heading_count():
    page = FakePage()
    page.role_locators[("heading", None, None)] = FakeLocator(
        children=[FakeLocator(), FakeLocator()]
    )

    assert assert_minimum_heading_count(page, 2) == 2
