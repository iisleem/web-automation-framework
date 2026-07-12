import pytest

from utils.helpers.i18n import (
    assert_locale_direction,
    assert_no_untranslated_keys,
    assert_page_direction,
    assert_page_locale,
    expected_direction_for_locale,
    normalize_locale,
    switch_language,
)


pytestmark = pytest.mark.helpers


class FakeLocator:
    def __init__(self, page, selector):
        self.page = page
        self.selector = selector
        self.selected = None

    def get_attribute(self, name):
        if self.selector == "html" and name == "lang":
            return self.page.lang
        if self.selector == "html" and name == "dir":
            return self.page.direction_attribute
        return None

    def inner_text(self):
        return self.page.body_text

    def select_option(self, value):
        self.selected = value
        self.page.lang = value
        self.page.direction_attribute = expected_direction_for_locale(value)


class FakePage:
    def __init__(self, lang="en-US", direction="ltr", body_text="Welcome"):
        self.lang = lang
        self.direction_attribute = direction
        self.body_text = body_text
        self.locators = {}

    def locator(self, selector):
        if selector not in self.locators:
            self.locators[selector] = FakeLocator(self, selector)
        return self.locators[selector]

    def evaluate(self, script):
        return expected_direction_for_locale(self.lang)


def test_locale_normalization_and_direction_mapping():
    assert normalize_locale("en_US") == "en-us"
    assert expected_direction_for_locale("ar-JO") == "rtl"
    assert expected_direction_for_locale("en-US") == "ltr"


def test_i18n_page_assertions_pass_for_matching_locale_and_direction():
    page = FakePage(lang="ar-JO", direction="rtl")

    assert_page_locale(page, "ar_jo")
    assert_page_direction(page, "rtl")
    assert_locale_direction(page, "ar-JO")


def test_i18n_assertions_report_mismatches():
    page = FakePage(lang="en-US", direction="ltr")

    with pytest.raises(AssertionError, match="Expected page locale"):
        assert_page_locale(page, "ar-JO")

    with pytest.raises(AssertionError, match="Expected page direction"):
        assert_page_direction(page, "rtl")


def test_untranslated_key_assertion_detects_leaked_keys():
    assert_no_untranslated_keys(FakePage(body_text="Welcome back"))

    with pytest.raises(AssertionError, match="Untranslated i18n keys"):
        assert_no_untranslated_keys(FakePage(body_text="common.checkout.title"))


def test_switch_language_selects_locale_and_validates_page_lang():
    page = FakePage(lang="en-US", direction="ltr")

    switch_language(page, "#language", "ar-JO")

    assert page.locator("#language").selected == "ar-JO"
    assert page.lang == "ar-JO"
    assert page.direction_attribute == "rtl"
